****************************************************
NITF File
****************************************************

This section describes the overall software design. You can
also :ref:`nitf-file-ref-section` for descriptions of the class member
functions.

We want to be able to read an write NITF files.

The NitfFile class structure is shown in :numref:`nitf_file`.

.. _nitf_file:
.. uml::
   :caption: NitfFile class structure

   class NitfFile {
      NitfFile(file_name=None,\n         security = security_unclassified,\n         use_raw=False)
      read(file_name, use_raw=False)
      write(file_name)
      NitfFileHeader file_header
      file_name
      NitfImageSegment image_segment[]
      NitfGraphicSegment graphic_segment[]
      NitfTextSegment text_segment[]
      NitfDesSegment des_segment[]
      NitfResSegment res_segment[]
      Tre tre_list[]
      security
   }
   note top
      The NITF file class, used for reading
      and writing a NITF file
   end note

   abstract class NitfSegment {
      +NitfFile nitf_file
      +subheader
      +user_subheader
      +Tre tre_list[]
      +data
   }
   note top
      Base class of NITF segments.

      Note not all segment types can have
      user_header or TREs. Just to prevent needing
      special handling for each segment type, we
      include this in all segment types but set to
      None (for user_subheader) or an empty list (for
      TREs) if the particular segment type doesn't
      support that.
   end note

   class NitfImageSegment {
      +Tre tre_list[]
   }

   class NitfGraphicSegment {
      +Tre tre_list[]
   }

   class NitfTextSegment {
      +Tre tre_list[]
   }

   class NitfDesSegment {
       +user_subheader
   }

   class NitfResSegment {
       +user_subheader
   }

   class Tre

   NitfSegment <|.. NitfImageSegment
   NitfSegment <|.. NitfGraphicSegment
   NitfSegment <|.. NitfTextSegment
   NitfSegment <|.. NitfDesSegment
   NitfSegment <|.. NitfResSegment
   NitfFile o-- "many" NitfImageSegment
   NitfFile o-- "many" NitfGraphicSegment
   NitfFile o-- "many" NitfTextSegment
   NitfFile o-- "many" NitfDesSegment
   NitfFile o-- "many" NitfResSegment
   NitfFile "file level" o-- "many" Tre
   NitfImageSegment o-- "many" Tre
   NitfTextSegment o-- "many" Tre
   NitfGraphicSegment o-- "many" Tre

Note that only NitfFile, NitfImageSegment, NitfTextSegment and
NitfGraphicSegment can have TREs. NitfResSegment and NitfDesSegment can not.
However, NitfResSegment
and NitfDesSegment can have a "user_subheader" supplied. The particular fields
in a user_subheader are determined by the desid or resid type identifier.

NitfFile Handles and Hooks
--------------------------

In addition to the NitfSegment, NitfFile contains several handle and hooks,
shown in :numref:`nitf_file_hook`.

.. _nitf_file_hook:
.. uml::
   :caption: NitfFile class Handles and Hooks

   class NitfFile {
      NitfSegmentHookSet segment_hook_set
      NitfSegmentUserSubheaderHandleSet user_subheader_handle_set
      NitfSegmentDataHandleSet data_handle_set
   }

   class NitfSegmentHookSet {
      +add_hook(h)
      +discard_hook(h)
      {static} add_default_hook(cls, h)
      {static} discard_default_hook(cls, h)
      {static} default_hook_set()
      }
   note top
     Hook objects to extend the handling
     of various attributes of a segments
     (e.g., add higher level classes Rpc
     or RSM).
   end note

   class NitfSegmentUserSubheaderHandleSet {
      +DesUserSubheaderHandleSet des_set
      +ResUserSubheaderHandleSet res_set
   }
   note bottom
      Handle reading and writing User 
      Subheaders for various segments.
   end note

   class NitfSegmentDataHandleSet {
     +NitfImageHandleSet image_handle_set
     +NitfDesHandleSet des_handle_set
     +NitfTextHandleSet text_handle_set
     +NitfGraphicHandleSet graphic_handle_set
     +NitfResHandleSet res_handle_set
   }
   note top
      Handle reading and writing the
      data in a segment (e.g, a image)
   end note

   NitfFile o--  NitfSegmentHookSet
   NitfFile o--  NitfSegmentUserSubheaderHandleSet
   NitfFile o--  NitfSegmentDataHandleSet

NitfSegmentHookSet
------------------

The NitfSegmentHookSet is used to extend the handling of various
attributes of a segment. The hooks are pretty general, and can be
used for whatever is desired. But the original use case was adding
higher level objects to NitfSegments such as RPC and RSM (done in
the separate GeoCal library).

The current set of higher level objects are:

.. table:: Higher level objects handled by various NitfSegmentHook
	   
  +-------------------+---------------------------------------------------+
  | Segment Attribute | Description                                       |
  +===================+===================================================+
  | rpc               | In GeoCal (not pynitf). This is a RPC (Rational   |
  |                   | Polynomial Coefficient. This is a common          |
  |                   | technique, and there are numerous references.     |
  |                   | One reference is Fraser, CS, Dial, G, Grodecki, J |
  |                   | "Sensor orientation via RPCs" ISPRS J PHOTOGRAMM  |
  |                   | 60 (3): 182-194 MAY 2006.                         |
  +-------------------+---------------------------------------------------+
  | rsm               | In GeoCal (not pynitf). This is a RSM (Replacement|
  |                   | Sensor Model), see Dolloff, J.T., M.M. Iiyama,    |
  |                   | and C.R. Taylor, 2008. The Replacement Sensor     |
  |                   | Model (RSM): Overview, Status, and Performance    |
  |                   | Summary, ASPRS 2008 Annual Conference, April 28 - |
  |                   | May 2, 2008                                       |
  +-------------------+---------------------------------------------------+

See :numref:`nitf_segment_hook`.

.. _nitf_segment_hook:
.. uml::
   :caption: NitfSegmentHookSet

   class NitfFile {
      NitfSegmentHookSet segment_hook_set
   }

   class NitfSegmentHookSet {
      +after_init_hook(seg, nitf_file)
      +before_write_hook(seg, nitf_file)
      +after_read_hook(seg, nitf_file)
      +before_str_hook(seg, nitf_file, fh)
      +before_str_tre_hook(seg, tre, nitf_file, fh)
      +add_hook(h)
      +discard_hook(h)
      {static} add_default_hook(cls, h)
      {static} discard_default_hook(cls, h)
      {static} default_hook_set()
      }
   note top
     Set of all the hook objects we use
     for a NitfFile.
   end note

   class NitfSegmentHook {
      +after_init_hook(seg, nitf_file)
      +before_write_hook(seg, nitf_file)
      +after_read_hook(seg, nitf_file)
      +before_str_hook(seg, nitf_file, fh)
      +before_str_tre_hook(seg, tre, nitf_file, fh)
      +remove_for_raw_print()
   }
   note bottom
      Hook object to extend handling of
      various attributes of a NitfSegment.
   end note
   
   NitfFile o--  NitfSegmentHookSet
   NitfSegmentHookSet o-- "many" NitfSegmentHook

We call all the NitfSegmentHook objects at several points in the processing:

* After NitfSegment.__init__ is called for a segment. This might do something
  like add a new attribute to the newly created segment (e.g., add "rpc")
* Before writing a NitfSegment to a file. This might translate a higher
  level object into TREs (e.g., for a RSM object).
* After reading a NitfSegment. This might create a object based on TREs
  (e.g., RSM based on various RSM Tres). Note this actually gets called
  after the entire file has been read, so if the objects depend on other
  later segments they are available (e.g., the orbit DESs for a
  GLAS/GFM object on a image segment)
* Before calling __str__ on a NitfSegment. This can be used to write out
  a higher level object (e.g., RPC, RSM).
* Before calling __str__ on a TRE. This can write a replacement text. Should
  return "True" if the TRE printing has been done by this function, "False"
  if the normal TRE printing should be done instead.

Note that when printing out a NitfSegment, most of the time we want the higher
level objects printed. However, there may be instances where we want the "raw"
data (e.g., nitfinfofull reporting raw TRE data). NitfSegmentHookSet will
skip calling before_str_hook and before_tre_str_hook if
"remove_for_raw_print" is True for the NitfSegmentHook.

NitfSegmentUserSubheaderHandleSet
---------------------------------

The NitfSegmentUserSubheaderHandleSet is used to handle reading and writing
the user subheaders found in the NitfDesSegment and NitfResSegment. This
contains a PriorityHandleSet (see :ref:`priority-handle-set-section`) for
handling each of these segment types. See :numref:`nitf_user_subheader_handle`.

.. _nitf_user_subheader_handle:
.. uml::
   :caption: NitfSegmentUserSubheaderHandleSet

   class NitfFile {
      NitfSegmentHookSet segment_hook_set
      NitfSegmentUserSubheaderHandleSet user_subheader_handle_set
      NitfSegmentDataHandleSet data_handle_set
   }

   class NitfSegmentHookSet {
      +add_hook(h)
      +discard_hook(h)
      {static} add_default_hook(cls, h)
      {static} discard_default_hook(cls, h)
      {static} default_hook_set()
      }
   note top
     Hook objects to extend the handling
     of various attributes of a segments
     (e.g., add higher level classes Rpc
     or RSM).
   end note

   class NitfSegmentHook
   
   class NitfSegmentUserSubheaderHandleSet {
      +DesUserSubheaderHandleSet des_set
      +ResUserSubheaderHandleSet res_set
   }
   note bottom
      Handle reading and writing User 
      Subheaders for various segments.
   end note

   class PriorityHandleSet

   class DesUserSubheaderHandleSet
   
   class ResUserSubheaderHandleSet
   
   class NitfSegmentDataHandleSet {
     +NitfImageHandleSet image_handle_set
     +NitfDesHandleSet des_handle_set
     +NitfTextHandleSet text_handle_set
     +NitfGraphicHandleSet graphic_handle_set
     +NitfResHandleSet res_handle_set
   }
   note top
      Handle reading and writing the
      data in a segment (e.g, a image)
   end note

   class NitfImageHandleSet
   class NitfDesHandleSet
   class NitfTextHandleSet
   class NitfGraphicHandleSet
   class NitfResHandleSet 
   
   NitfFile o--  NitfSegmentHookSet
   NitfFile o--  NitfSegmentUserSubheaderHandleSet
   NitfFile o--  NitfSegmentDataHandleSet
   NitfSegmentHookSet o-- "many" NitfSegmentHook
   NitfSegmentUserSubheaderHandleSet o-- "many" DesUserSubheaderHandleSet
   NitfSegmentUserSubheaderHandleSet o-- "many" ResUserSubheaderHandleSet
   NitfSegmentDataHandleSet o-- "many" NitfImageHandleSet
   NitfSegmentDataHandleSet o-- "many" NitfDesHandleSet
   NitfSegmentDataHandleSet o-- "many" NitfTextHandleSet
   NitfSegmentDataHandleSet o-- "many" NitfGraphicHandleSet
   NitfSegmentDataHandleSet o-- "many" NitfResHandleSet
   NitfSegmentUserSubheaderHandleSet -[hidden]- PriorityHandleSet
   NitfSegmentDataHandleSet -[hidden]- PriorityHandleSet
   DesUserSubheaderHandleSet -[hidden]- NitfImageHandleSet
   DesUserSubheaderHandleSet -[hidden]- NitfDesHandleSet
   DesUserSubheaderHandleSet -[hidden]- NitfTextHandleSet
   DesUserSubheaderHandleSet -[hidden]- NitfGraphicHandleSet
   DesUserSubheaderHandleSet -[hidden]- NitfResHandleSet
   PriorityHandleSet <|-- DesUserSubheaderHandleSet
   PriorityHandleSet <|-- ResUserSubheaderHandleSet
   PriorityHandleSet <|-- NitfImageHandleSet
   PriorityHandleSet <|-- NitfDesHandleSet
   PriorityHandleSet <|-- NitfTextHandleSet
   PriorityHandleSet <|-- NitfGraphicHandleSet
   PriorityHandleSet <|-- NitfResHandleSet

NitfSegmentDataHandleSet
---------------------------------

The NitfSegmentDataHandleSet is used to handle reading and writing
the data field of each of the NitfSegment types. This
contains a PriorityHandleSet (see :ref:`priority-handle-set-section`) for
handling
each of these segment types. See :numref:`nitf_data_handle`.

.. _nitf_data_handle:
.. uml::
   :caption: NitfSegmentDataHandleSet

   class NitfFile {
      NitfSegmentHookSet segment_hook_set
      NitfSegmentUserSubheaderHandleSet user_subheader_handle_set
      NitfSegmentDataHandleSet data_handle_set
   }

   class NitfSegmentHookSet {
      +add_hook(h)
      +discard_hook(h)
      {static} add_default_hook(cls, h)
      {static} discard_default_hook(cls, h)
      {static} default_hook_set()
      }
   note top
     Hook objects to extend the handling
     of various attributes of a segments
     (e.g., add higher level classes Rpc
     or RSM).
   end note

   class NitfSegmentHook
   
   class NitfSegmentUserSubheaderHandleSet {
      +DesUserSubheaderHandleSet des_set
      +ResUserSubheaderHandleSet res_set
   }
   note bottom
      Handle reading and writing User 
      Subheaders for various segments.
   end note

   class PriorityHandleSet

   class DesUserSubheaderHandleSet
   
   class ResUserSubheaderHandleSet
   
   class NitfSegmentDataHandleSet {
     +NitfImageHandleSet image_handle_set
     +NitfDesHandleSet des_handle_set
     +NitfTextHandleSet text_handle_set
     +NitfGraphicHandleSet graphic_handle_set
     +NitfResHandleSet res_handle_set
   }
   note top
      Handle reading and writing the
      data in a segment (e.g, a image)
   end note

   class NitfImageHandleSet
   class NitfDesHandleSet
   class NitfTextHandleSet
   class NitfGraphicHandleSet
   class NitfResHandleSet 
   
   NitfFile o--  NitfSegmentHookSet
   NitfFile o--  NitfSegmentUserSubheaderHandleSet
   NitfFile o--  NitfSegmentDataHandleSet
   NitfSegmentHookSet o-- "many" NitfSegmentHook
   NitfSegmentUserSubheaderHandleSet o-- "many" DesUserSubheaderHandleSet
   NitfSegmentUserSubheaderHandleSet o-- "many" ResUserSubheaderHandleSet
   NitfSegmentDataHandleSet o-- "many" NitfImageHandleSet
   NitfSegmentDataHandleSet o-- "many" NitfDesHandleSet
   NitfSegmentDataHandleSet o-- "many" NitfTextHandleSet
   NitfSegmentDataHandleSet o-- "many" NitfGraphicHandleSet
   NitfSegmentDataHandleSet o-- "many" NitfResHandleSet
   NitfSegmentUserSubheaderHandleSet -[hidden]- PriorityHandleSet
   NitfSegmentDataHandleSet -[hidden]- PriorityHandleSet
   DesUserSubheaderHandleSet -[hidden]- NitfImageHandleSet
   DesUserSubheaderHandleSet -[hidden]- NitfDesHandleSet
   DesUserSubheaderHandleSet -[hidden]- NitfTextHandleSet
   DesUserSubheaderHandleSet -[hidden]- NitfGraphicHandleSet
   DesUserSubheaderHandleSet -[hidden]- NitfResHandleSet
   PriorityHandleSet <|-- DesUserSubheaderHandleSet
   PriorityHandleSet <|-- ResUserSubheaderHandleSet
   PriorityHandleSet <|-- NitfImageHandleSet
   PriorityHandleSet <|-- NitfDesHandleSet
   PriorityHandleSet <|-- NitfTextHandleSet
   PriorityHandleSet <|-- NitfGraphicHandleSet
   PriorityHandleSet <|-- NitfResHandleSet
   


NitfFile convenience functions
------------------------------

While the individual lists can be filters/searched using normal python
functions, there are a set of things done frequently enough that it is
useful to add convenience functions to do them. These are shown in
in :numref:`nitf_file_convenience`.

.. _nitf_file_convenience:
.. uml::
   :caption: NitfFile Convenience Functions

   class NitfFile {
      +engrda
      +find_tre(tre_tag)
      +find_one_tre(tre_tag)
      +find_exactly_one_tre(tre_tag)
      +iseg_by_idlv(idlvl)
      +iseg_by_iid1(iid1)
      +iseg_by_iid1_single(iid1)
   }

   note left of NitfFile::engrda
      ENGRDA data returned as a
      dict like interface (e.g.,
      f.engrda["My_sensor 1"]["TEMP1"])

      Both reading and setting values
      supported
   end note
   note right of NitfFile::find_tre
      Return list of TREs of the
      given tag. Possibly empty
   end note
   note right of NitfFile::find_one_tre
      Find at most one TRE of the
      given tag. Return None if not
      found, error if multiple found
   end note
   note right of NitfFile::find_exactly_one_tre
      Like find_one_tre, but not finding
      TRE is treated as an error.
   end note

   class NitfImageSegment {
      +engrda
      +find_tre(tre_tag)
      +find_one_tre(tre_tag)
      +find_exactly_one_tre(tre_tag)
   }

   class NitfTextSegment {
      +engrda
      +find_tre(tre_tag)
      +find_one_tre(tre_tag)
      +find_exactly_one_tre(tre_tag)
   }
   
   class NitfGraphicSegment {
      +engrda
      +find_tre(tre_tag)
      +find_one_tre(tre_tag)
      +find_exactly_one_tre(tre_tag)
   }
   NitfFile o-- "many" NitfImageSegment
   NitfFile o-- "many" NitfGraphicSegment
   NitfFile o-- "many" NitfTextSegment
   

