****************************************************
Software Design
****************************************************

Priority Set
---------------

We have a number of places where we want to have a 
`chain-of-responsibility <https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern>`_, with the addition of an ordering based on a priority order. We
also want to be able to modify the handles, starting with a default set of
handles. So for example while reading a NitfFile we would like to process
images using a set of handles (e.g., read JPEG 2000, read using numpy arrays,
etc.), that we could potentially change for a particular NitfFile (e.g.,
add a special reader for an unusual format).

To support this, we have a class PrioritySet. This is very similar to
a `priority queue <https://en.wikipedia.org/wiki/Priority_queue>`_ except that
we:

* Don't want to actually pop from a queue, rather we iterate through the stored
  items.
* The items aren't totally ordered. We iterate through items with the same
  priority in an arbitrary order
* We want to have a default list of handlers, that can then be modified.

The design for this is shown in :numref:`priority_set`.

.. _priority_set:
.. uml::
   :caption: Priority Set

   abstract class PrioritySet {
      +add_handle(h, priority_order=0)
      +discard_handle(h)
      {static} add_default_handle(cls, h, priority_order=0)
      {static} discard_default_handle(cls, h, priority_order=0)
      {static} default_handle_list()
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

   note right of PrioritySet::handle_h
      Determine if a given handle h can handle the
      given args. If it can, return (True, other_ret)
      otherwise, return (False, None).

      handle loops through all the handles h calling
      handle_h defined in the derived class, and returns
      the value returned by the first handle that says it
      could process that
   end note

   class NitfDesHandleSet
   note top
      Process NitfDes
   end note

   class NitfImageHandleSet
   note right
      Process NitfImage
   end note

   PrioritySet <|.. NitfDesHandleSet
   PrioritySet <|.. NitfImageHandleSet

nitf_diff
---------------
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
      +run(fname1, fname2)
   }
   note top
      This class contains a general dict "config"
      that can be used by any of the handles to
      record whatever.

      There is a NitfDiffHandleSet "handle_set"
      available, which contains the list of handles
      used to compare two objects.

      Both of these
   end note

   abstract class PrioritySet

   class NitfDiffHandleSet {
      +handle_h(h, nitf_diff, obj1, obj2)
      {static} default_config
   }
   note top
      Handle comparing two objects. Logs differences,
      and return True if the objects are the same, False
      if different.
   end note

   PrioritySet <|.. NitfDiffHandleSet
   NitfDiff *-- NitfDiffHandleSet : Has a handle_set

Most of the time there is a known set of handles and configuration parameters,
with a user adding or modifying a few. So we have both the default handles
for NitfDiffHandleSet and default configuration. NitfDiff
