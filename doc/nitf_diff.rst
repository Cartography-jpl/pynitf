****************************************************
NITF File Differences
****************************************************

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
	   
  +----------------------+-------------------------------------------------+
  | Class                | Description                                     |
  +======================+=================================================+
  | NitfFileHandle       | Top level class that handles comparing NitfFile |
  |                      | Compares matching items, so first image segment |
  |  		         | in file 1 compared to first image segment in    |
  |		         | file 2, etc. We could create more sophisticated |
  |	   	         | classes (e.g., compare by matching iid1), which |
  |                      | is why even the files are handled by a plugin   |
  +----------------------+-------------------------------------------------+
  | AlwaysTrueHandle     | Always say things are equal. Nice for various   |
  |                      | test cases (e.g. test some object types, skip   |
  |                      | other types).                                   |
  +----------------------+-------------------------------------------------+
  | FieldStructDiff      | Base class for various FieldStruct objects      |
  |                      | (e.g DiffFileHeader ).                          |
  +----------------------+-------------------------------------------------+
  | DiffFileHeader       | Compare NitfFileHeader.                         |
  +----------------------+-------------------------------------------------+
  | DesObjectDiff        | Compare NitfDesObjectHandle.                    |
  +----------------------+-------------------------------------------------+
  | DesPlaceHolderDiff   | Compare NitfDesPlaceHolder.                     |
  +----------------------+-------------------------------------------------+
  | CsattaDiff           | Compare DesCSATTA.                              |
  +----------------------+-------------------------------------------------+
  | CsattbDiff           | Compare DesCSATTB.                              |
  +----------------------+-------------------------------------------------+
  | CsattbUserheaderDiff | Compare DesCSATTB_UH.                           |
  +----------------------+-------------------------------------------------+
  | CsscdbDiff           | Compare DesCSSCDB.                              |
  +----------------------+-------------------------------------------------+
  | CsscdbUserheaderDiff | Compare DesCSSCDB_UH.                           |
  +----------------------+-------------------------------------------------+
  | CsephbDiff           | Compare DesCSEPHB.                              |
  +----------------------+-------------------------------------------------+
  | CsephbUserheaderDiff | Compare DesCSEPHB_UH.                           |
  +----------------------+-------------------------------------------------+
  | CssfabDiff           | Compare DesCSSFAB.                              |
  +----------------------+-------------------------------------------------+
  | CssfabUserheaderDiff | Compare DesCSSFAB_UH.                           |
  +----------------------+-------------------------------------------------+
  |  DesSubheaderDiff    | Compare NitfDesSubheader.                       |
  +----------------------+-------------------------------------------------+
  | ImagePlaceHolderDiff | Compare NitfImagePlaceHolder.                   |
  +----------------------+-------------------------------------------------+
  | ImageReadNumpyDiff   | Compare NitfImageReadNumpy.                     |
  +----------------------+-------------------------------------------------+
  | ImageSubheaderDiff   | Compare NitfImageSubheader.                     |
  +----------------------+-------------------------------------------------+
  | TextSubheaderDiff    | Compare NitfTextSubheader.                      |
  +----------------------+-------------------------------------------------+
  | TreDiff              | Compare Tre.                                    |
  +----------------------+-------------------------------------------------+
  | TreUnknownDiff       | Compare TreUnknown.                             |
  +----------------------+-------------------------------------------------+

The handles should return an overall status of the comparison, so True for
objects are the same, False otherwise.

Nitf difference logging
-----------------------

In addition to an overall status results, differences should be
reported to the users. We do this through the python logger:

.. code-block:: python

   logger = logging.getLogger("nitf-diff")

   logger.difference("This is a difference")
   logger.difference_ignored("This difference is reported but ignored")
   logger.difference_detail("This is more detailed information about differences")

The functions "difference", "difference_ignored" and
"difference_detail" have the same arguments as python logger "info".

While we could add new level names using
`logging.addLevelName <https://docs.python.org/3/library/logging.html#logging.addLevelName>`_
the python documentation
`points out <https://docs.python.org/3/howto/logging.html#custom-levels>`_
that this is a global namespace. We don't want to have any other library
that uses pynitf forced to use the new level names. So instead, we have a
special formatter DifferenceFormatter that handles this without adding
new names.

To display the new levels, DifferenceFormatter should be used as the formatter:

.. code-block:: python
		
   logger = logging.getLogger('nitf_diff')
   h = logging.StreamHandler()
   h.setFormatter(DifferenceFormatter())
   logger.addHandler(h)

Note to see detailed information about differences you should set the
logging level (in both the handler and the logger) to logging.INFO:

.. code-block:: python
		
    h.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

If for whatever reason the specific level choosen for the new levels
causes a problem you can redefine the levels used by changing the value
of "DIFFERENCE_FOUND", "DIFFERENCE_FOUND_BUT_IGNORED" and "DIFFERENCE_DETAIL"

Internally, we use a logging filter DiffContextFilter to pass the context
of the differences (e.g., "NITF File Header", "Image Segment 'blah', TRE 'blahblah'). You can use the the context manager in NitfDiff called diff_context
for setting this.
    
FieldStructDiff
---------------
  
There are various handles to check the different FieldStruct objects.

While we could just create new NitfDiffHandle objects for each field
structure (e.g., each of the TREs in the file), we instead try to
provide a good deal of functionality through "configuration". The
configuration is a dictionary type object that derived class get from
the nitf_diff object.  This then contains keyword/value pairs for
controlling things. While derived classes can supply other parameters,
these are things that can be defined:

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
the difference found at the logging level of DIFFERENCE_DETAIL.

   
