# This contains the top level object for reading and writing a NITF file.
#
# The class structure is a little complicated, so you can look and the UML
# file doc/Nitf_file.xmi (e.g., use umbrello) to see the design.

from .nitf_file_header import NitfFileHeader
from .nitf_tre import read_tre, prepare_tre_write, add_find_tre_function
from .nitf_tre_engrda import add_engrda_function
from .nitf_security import security_unclassified
from .nitf_segment import (NitfImageSegment, NitfGraphicSegment,
                           NitfTextSegment, NitfDesSegment,
                           NitfResSegment)
from .nitf_segment_hook import NitfSegmentHookSet
from .nitf_segment_user_subheader_handle import NitfSegmentUserSubheaderHandleSet
from .nitf_segment_data_handle import NitfSegmentDataHandleSet
import io,copy,weakref
import copy
import collections

class ListNitfFileReference(collections.UserList):
    '''Useful to add nitf_file to various NitfSegment as they get added
    to a NitfFile, so we override append'''
    def __init__(self, f, initlist = None):
        super().__init__(initlist)
        self.nitf_file = weakref.ref(f)
    def append(self, v):
        super().append(v)
        v._nitf_file = self.nitf_file
        if(v.nitf_file):
            v.nitf_file.segment_hook_set.after_append_hook(v, v.nitf_file)
        
class NitfFile(object):
    '''This is used to read and write a NITF File.

       :ivar file_header:      The NitfFileHeader for the file
       :ivar file_name:        The NITF file name
       :ivar segment_hook_set: The NitfSegmentHookSet to use for the file.
       :ivar user_subheader_handle_set: The NitfSegmentUserSubheaderHandleSet
                               to use for this file
       :ivar data_handle_set:  The NitfSegmentDataHandleSet to use for this
                               file
       :ivar report_raw:       If True, suppress NitfSegmentHook when printing
       :ivar image_segment:    List of NitfImageSegment objects for the file.
       :ivar graphic_segment:  List of NitfGraphicSegment objects for the file.
       :ivar text_segment:     List of NitfTextSegment objects for the file.
       :ivar des_segment:      List of NitfDesSegment objects for the file.
       :ivar res_segment:      List of NitfResSegment objects for the file.
       :ivar tre_list:         List of Tre objects for the file level TREs.

    '''        
    def __init__(self, file_name = None, security = security_unclassified):
        '''Create a NitfFile for reading or writing. Because it is common, if
        you give a file_name we read from that file to populate the Nitf 
        structure. Otherwise we start with a default file (a file header, but
        no segments) - which you can then populate before calling write'''
        self.file_header = NitfFileHeader()
        self.file_name = file_name
        self.report_raw = False
        self.segment_hook_set = copy.copy(NitfSegmentHookSet.default_hook_set())
        self.user_subheader_handle_set = copy.copy(NitfSegmentUserSubheaderHandleSet.default_handle_set())
        self.data_handle_set = copy.copy(NitfSegmentDataHandleSet.default_handle_set())
        # This is the order things appear in the file
        self.image_segment = ListNitfFileReference(self)
        self.graphic_segment = ListNitfFileReference(self)
        self.text_segment = ListNitfFileReference(self)
        self.des_segment = ListNitfFileReference(self)
        self.res_segment = ListNitfFileReference(self)
        # These are the file level TREs. There can also be TREs at the
        # image segment level
        self.tre_list = []
        if(file_name is not None):
            self.read(file_name)
        if(file_name is None):
            self.security = security

    def __str__(self):
        '''Text description of structure, e.g., something you can print out'''
        res = io.StringIO()
        print("-------------------------------------------------------------",
              file=res)
        print("File Header:", file=res)
        print(self.file_header, file=res)
        print("-------------------------------------------------------------",
              file=res)
        if(len(self.tre_list) == 0):
            print("No file level TREs", file=res)
        else:
            print("File level TRES:", file=res)
            for t in self.tre_list:
                print(t, file=res)
            print("-------------------------------------------------------------",
                  file=res)
        for arr, name in [[self.image_segment, "Image"],
                          [self.graphic_segment, "Graphic"],
                          [self.text_segment, "Text"],
                          [self.des_segment, "Data Extension"],
                          [self.res_segment, "Reserved Extension"]]:
            if(len(arr) == 0):
                print("No %s segments" % name, file=res)
            else:
                print("-------------------------------------------------------------",
                      file=res)
            for i, seg in enumerate(arr):
                print("%s segment %d of %d" % (name, i+1, len(arr)),
                      file=res)
                print(seg,end='',file=res)
                print("-------------------------------------------------------------",
                      file=res)
        return res.getvalue()
    def summary(self):
        '''Short text summary of this file, something you can print out'''
        res = io.StringIO()
        print("NITF File Summary", file=res)
        print("-------------------------------------------------------------",
              file=res)
        print("File Header:", file=res)
        print(self.file_header.summary(), file=res, end='', flush=True)
        print("-------------------------------------------------------------",
              file=res)
        if(len(self.tre_list) == 0):
            print("No file level TREs", file=res)
        else:
            print("File level TRES:", file=res)
            for t in self.tre_list:
                print(t.summary(), file=res, end='', flush=True)
            print("-------------------------------------------------------------",
                  file=res)
        for arr, name in [[self.image_segment, "Image"],
                          [self.graphic_segment, "Graphic"],
                          [self.text_segment, "Text"],
                          [self.des_segment, "Data Extension"],
                          [self.res_segment, "Reserved Extension"]]:
            if(len(arr) == 0):
                print("No %s segments" % name, file=res)
            else:
                print("-------------------------------------------------------------",
                      file=res)
            for i, seg in enumerate(arr):
                print("%s segment %d of %d" % (name, i+1, len(arr)),
                      file=res)
                print(seg.summary(),end='',file=res, flush=True)
                print("-------------------------------------------------------------",
                      file=res)
        return res.getvalue()
    def read(self, file_name):
        '''Read the given file.'''
        self.file_name = file_name
        with open(file_name, 'rb') as fh:
            self.file_header.read_from_file(fh)
            # We don't currently support streaming file format. This is
            # indicated by fl being 999999999999 (the maximum file size
            # allowed is 999999999998). Report this. We could perhaps add
            # support for this if needed, but for now just catch that we
            # encountered this and give up
            if(self.file_header.fl == 999999999999):
                raise RuntimeError("We don't currently support reading streaming NITF files")
            self.image_segment = \
               [NitfImageSegment(header_size=self.file_header.lish[i],
                                 data_size=self.file_header.li[i],
                                 nitf_file = self) for i in
                range(self.file_header.numi)]
            self.graphic_segment = \
               [NitfGraphicSegment(header_size=self.file_header.lssh[i],
                                   data_size=self.file_header.ls[i],
                                   nitf_file = self) for i in
                range(self.file_header.nums)]
            self.text_segment = \
               [NitfTextSegment(header_size=self.file_header.ltsh[i],
                                data_size=self.file_header.lt[i],
                                nitf_file = self) for i in
                range(self.file_header.numt)]
            self.des_segment = \
               [NitfDesSegment(header_size=self.file_header.ldsh[i],
                               data_size=self.file_header.ld[i],
                               nitf_file = self) for i in
                range(self.file_header.numdes)]
            self.res_segment = \
               [NitfResSegment(header_size=self.file_header.lresh[i], 
                               data_size=self.file_header.lre[i],
                               nitf_file = self) for i in
                range(self.file_header.numres)]
            for i, seg in self.segments(include_seg_index=True):
                seg.read_from_file(fh, i)
            self.tre_list = read_tre(self.file_header, self.des_segment,
                                     [["xhdl", "xhdlofl", "xhd"],
                                      ["udhdl", "udhofl", "udhd"]])
            for seg in self.segments():
                seg.read_tre(self.des_segment)
            for seg in self.segments():
                self.segment_hook_set.after_read_hook(seg, self)
    def write(self, file_name):
        '''Write to the given file'''
        for seg in self.segments():
            self.segment_hook_set.before_write_hook(seg, self)
        self.des_segment = \
            ListNitfFileReference(self, [dseg for dseg in self.des_segment
                                   if(dseg.subheader.desid.encode("utf-8") !=
                                      b'TRE_OVERFLOW')])
        with open(file_name, 'w+b') as fh:
            h = self.file_header
            prepare_tre_write(self.tre_list, h, self.des_segment,
                              [["xhdl", "xhdlofl", "xhd"],
                               ["udhdl", "udhofl", "udhd"]])
            for i, seg in self.segments(include_seg_index=True):
                seg.prepare_tre_write(i, self.des_segment)
            h.numi = len(self.image_segment)
            h.nums = len(self.graphic_segment)
            h.numt = len(self.text_segment)
            h.numdes = len(self.des_segment)
            h.numres = len(self.res_segment)
            h.write_to_file(fh)
            # Might be a cleaner way to do this, but for now we just "know"
            # we need to update the header length
            h.update_field(fh, "hl", fh.tell())
            # Write out each segment, updating the subheader and data sizes
            for i, seg in self.segments(include_seg_index=True):
                seg.write_to_file(fh, i)
            # Now we have to update the file length
            h.update_field(fh, "fl", fh.tell())
        # Special handling for the TRE overflow DES. We create these as
        # needed for the TREs that we already have stored various places.
        # Clear out any that generated during our write
        self.des_segment = \
            ListNitfFileReference(self, [dseg for dseg in self.des_segment
                                   if(dseg.subheader.desid.encode("utf-8") !=
                                      b'TRE_OVERFLOW')])

    def segments(self, include_seg_index=False):
        '''Iterator to go through all the segments in a file. We often also
        need the seg_index, so you can pass that as True and we return the
        pair (seg_index, seg). 

        Note that although this goes through all the segment types, the 
        seg_index is relative to the segment type. So for example, the
        first graphic segment returns (0, gseg_0) even though this might
        be the 10th segment in the file. This is just the way that NITF
        wants these listed.

        Just to avoid confusion, the seg_index are always 0 based. NITF Files
        tend to use 1 based indexing, we handle the conversion to and from
        1 based indexing at the lowest level of the file access.
        '''
        for seglist in [self.image_segment, self.graphic_segment, 
                        self.text_segment, self.des_segment,
                        self.res_segment]:
            for i, seg in enumerate(seglist):
                if(include_seg_index):
                    yield(i, seg)
                else:
                    yield seg
                    

    def iseg_by_idlvl(self, idlvl):
        '''Return the image segment with a idlvl matching the given id'''
        for iseg in self.image_segment:
            if(iseg.idlvl == idlvl):
                return iseg
        raise KeyError(str(id))

    def iseg_by_iid1(self, iid1):
        '''Return a (possibly empty) list of image segments with the given
        iid1 value.'''
        return [iseg for iseg in self.image_segment if iseg.iid1 == iid1]

    def iseg_by_iid1_single(self,iid1):
        '''Return a single match to the given iid1. If we have 0 or more than
        1 match, then this throws an error.'''
        t = self.iseg_by_iid1(iid1)
        if(len(t) == 0):
            raise KeyError(iid1)
        if(len(t) > 1):
            raise RuntimeError("More than one match found to iid1='%s'" % iid1)
        return t[0]

    @property
    def security(self):
        '''NitfSecurity for file.'''
        return self.file_header.security

    @security.setter
    def security(self, v):
        '''Set NitfSecurity for file.'''
        self.file_header.security = v

# Add engrda to give hash access to ENGRDA TREs
add_engrda_function(NitfFile)

# Add TRE finding functions
add_find_tre_function(NitfFile)
    
__all__ = ["NitfFile", ]
