****************************************************
Software Design
****************************************************

Priority Handle Set
-------------------

We have a number of places where we want to have a 
`chain-of-responsibility <https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern>`_, with the addition of an ordering based on a priority order. We
also want to be able to modify the handles, starting with a default set of
handles. So for example while reading a NitfFile we would like to process
images using a set of handles (e.g., read JPEG 2000, read using numpy arrays,
etc.), that we could potentially change for a particular NitfFile (e.g.,
add a special reader for an unusual format).

To support this, we have a class PriorityHandleSet. This is very similar to
a `priority queue <https://en.wikipedia.org/wiki/Priority_queue>`_ except that
we:

* Don't want to actually pop from a queue, rather we iterate through the stored
  items.
* The items aren't totally ordered. We iterate through items with the same
  priority in an arbitrary order
* We want to have a default list of handlers, that can then be modified.

The design for this is shown in :numref:`priority_handle_set`.

.. _priority_handle_set:
.. uml::
   :caption: Priority Handle Set

   abstract class PriorityHandleSet {
      +add_handle(h, priority_order=0)
      +discard_handle(h)
      {static} add_default_handle(cls, h, priority_order=0)
      {static} discard_default_handle(cls, h, priority_order=0)
      {static} default_handle_set()
      +handle(*args, **keywords)
      {abstract} handle_h(h, *args, **keywords)
   }
   note top
      This class also adds the normal python
      magic functions to be able to iterate like
      a set.

      Higher numbers in the priority order are
      returned first.

      We also have proper copy semantics, so you
      can call copy.copy(t.default_handle_set())
      to get a copy of the default set that can be
      modified.
   end note

   class NitfDesHandleSet
   note top
      Process NitfDes
   end note

   class NitfImageHandleSet
   note right
      Process NitfImage
   end note

   PriorityHandleSet <|-- NitfDesHandleSet
   PriorityHandleSet <|-- NitfImageHandleSet

The PriorityHandleSet has members for adding and removing "Handles". A handle
is purposely vague, it is any object that the derived class wants to be.
And in some cases the object is actually a class - so for example
NitfImageHandleSet uses handles that are classes derived from NitfImage.

The function handle forwards work to the function handle_h, as shown in
:numref:`handle_sequence`

.. _handle_sequence:
.. uml::
   :caption: handler_set:DerivedFromPriorityHandleSet sequence diagram

   caller -> "handler_set:DerivedFromPriorityHandleSet" as hset: 1 handle(*args, **keywords)
   loop h:HandleObjects
       hset -> hset : 1.1 handle_h(h,*args,**keywords)
       alt h couldn't handle
          hset -> hset: return (False, None)
       else h could handle
          hset -> hset: return (True, res)
       end
       note right hset
          Continue looping until the
	  first h can handle the args
       end note
   end
   
nitf_diff
---------
We want to be able compare two NITF files to know if they are the "same".

What is the "same" really depends on the application. For example, two files
with images that have a difference of 1e-4 might be different because the data
isn't identical, or might be the same because they are close enough.

Likewise, if we generate GLAS/GFM DESs, we don't expect the UUIDs to be the
same between 2 runs, even if the actual GLAS/GFM is the "same". And the file
date time (fdt) will generally change from one run to the next.

The output from nitf_diff will be an overall status code (normal or 0 exit code
for identical, 1 for different), along with log information describing
what if any differences there are.

We use the same pluggable set of handles like we do for NitfDesHandleSet etc.
The design is shown in :numref:`nitf_diff`.

.. _nitf_diff:
.. uml::
   :caption: nitf_diff

   class NitfDiff {
      +config
      +handle_set
      +compare(fname1, fname2)
      +compare_obj(self, obj1, obj2)
   }
   note top
      This class contains a general dict "config"
      that can be used by any of the handles to
      record whatever.

      There is a NitfDiffHandleSet "handle_set"
      available, which contains the list of handles
      used to compare two objects.

      Both of these are set to initial default values
      stored in NitfDiffHandleSet class.
   end note

   abstract class PriorityHandleSet

   class NitfDiffHandleSet {
      +handle_h(h, nitf_diff, obj1, obj2)
      {static} default_config
   }
   note bottom
      Handle comparing two objects. Logs differences,
      and return True if the objects are the same, False
      if different.
   end note

   class NitfDiffHandle {
     +handle_diff(self, obj1, obj2, nitf_diff)
   }
   note bottom
      Base class for handling difference between
      two NITF object. Like always, you don't
      need to actually derive from this class if
      for whatever reason this isn't convenient
      but you should provide this interface.

      handle_diff returns (False, None) if it can't
      handle obj1 and obj2, (True, Comparison_result)
      if it can. Comparison_result is True if objects
      are the "same", False otherwise.
   end note

   PriorityHandleSet <|-- NitfDiffHandleSet
   NitfDiff *-- NitfDiffHandleSet : Has a handle_set
   NitfDiffHandleSet *-- "many" NitfDiffHandle
   
Most of the time there is a known set of handles and configuration parameters,
with a user adding or modifying a few. So we have both the default handles
for NitfDiffHandleSet and default configuration. NitfDiff object can then
have their handle and/or config objects modified to change the behavior for
a specific comparison. The program nitf_diff (which is a wrapper around
NitfDiff) can take a JSON file and/or arbitrary python code to change this.

NitfDiffHandle
--------------

There are a number of NitfDiffHandle objects defined in pynitf:

.. table:: NitfDiffHandle objects
	   
  +---------------------+-------------------------------------------------+
  | Class               | Description                                     +
  +=====================+=================================================+
  | NitfFileHandle      | Top level class that handles comparing NitfFile |
  |                     | Compares matching items, so first image segment |
  |  		        | in file 1 compared to first image segment in    |
  |		        | file 2, etc. We could create more sophisticated |
  |	   	        | classes (e.g., compare by matching iid1), which |
  |                     | is why even the files are handled by a plugin   |
  +---------------------+-------------------------------------------------+
  | AlwaysTrueHandle    | Always say things are equal. Nice for various   |
  |                     | test cases (e.g. test some object types, skip   |
  |                     | other types).                                   |
  +---------------------+-------------------------------------------------+
  | FieldStructDiff     | Base class for various FieldStruct objects      |
  |                     | (e.g DiffFileHeader )                           |
  +---------------------+-------------------------------------------------+
  | DiffFileHeader      | Compare NitfFileHeader                          |
  +---------------------+-------------------------------------------------+

FieldStructDiff
---------------
  
There are various handles to check the different FieldStruct objects.

While we could just create new NitfDiffHandle objects for each
field structure (e.g., each of the TREs in the file), we instead try to
provide a good deal of functionality through "configuration". The
configuration is a dictionary type object that derived class get
from the nitf_diff object.  This then contains keyword/value pairs
for controlling things. While derived classes can others, these
are things that can be defined:

* **exclude** - List of fields to exclude from comparing
* **exclude_but_warn** - List of field to exclude from comparing, but
  warn if different.
* **include** - If nonempty, only include the given fields
* **eq_fun** - A dictionary going from field name to a function to compare.
* **rel_tol** - A dictionary going from field name to a relative tolerance.
  Only used for fields with float type.
* **abs_tol** - A dictionary going from field name to absolute tolerance.
  Only used for fields with float type.

If a function isn't otherwise defined in eq_fun, we use operator.eq, 
except for floating point numbers. For floating point numbers we use
math.isclose. The rel_tol and/or abs_tol can be supplied. The default
values are used for math.isclose if not supplied (so 1e-9 and 0.0).
    
For array/loop fields we compare the shape, and if the same we compare
each element in the array. The default it to provide a summary of differences
(e.g., array had 1 of 42 difference). We also provide information about all
the difference found at the logging level of INFO.

   
