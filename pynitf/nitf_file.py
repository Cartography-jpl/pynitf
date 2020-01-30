# This contains the top level object for reading and writing a NITF file.
#
# The class structure is a little complicated, so you can look and the UML
# file doc/Nitf_file.xmi (e.g., use umbrello) to see the design.

from __future__ import print_function
from .nitf_file_header import NitfFileHeader
from .nitf_image import NitfImageHandleSet
from .nitf_des import NitfDesHandleSet
from .nitf_tre import read_tre, prepare_tre_write, add_find_tre_function
from .nitf_tre_engrda import add_engrda_function
from .nitf_security import security_unclassified
from .nitf_segment import (NitfImageSegment, NitfGraphicSegment,
                           NitfTextSegment, NitfDesSegment,
                           NitfResSegment)
import io,six,copy,weakref
import copy
import collections

class ListNitfFileReference(collections.UserList):
    '''Useful to add nitf_file to various NitfSegment as they get added
    to a NitfFile, so we override append'''
    def __init__(self, f):
        super().__init__()
        self.nitf_file = weakref.ref(f)
    def append(self, v):
        super().append(v)
        v._nitf_file = self.nitf_file
        
class NitfFile(object):
    # List of hook objects to extend the handling in the various types of
    # segments. Right now we only do this for image_segment and text_segment,
    # but we could extend this if desired
    image_segment_hook_obj = []
    des_segment_hook_obj = []
    text_segment_hook_obj = []
    def __init__(self, file_name = None, security = security_unclassified,
                 use_raw = False):
        '''Create a NitfFile for reading or writing. Because it is common, if
        you give a file_name we read from that file to populate the Nitf 
        structure. Otherwise we start with a default file (a file header, but
        no segments) - which you can then populate before calling write'''
        self.file_header = NitfFileHeader()
        self.file_name = file_name
        self.image_handle_set = copy.copy(NitfImageHandleSet.default_handle_set())
        self.des_handle_set = copy.copy(NitfDesHandleSet.default_handle_set())
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
            self.read(file_name, use_raw=use_raw)
        if(file_name is None):
            self.security = security

    def __str__(self):
        '''Text description of structure, e.g., something you can print out'''
        res = six.StringIO()
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
        res = six.StringIO()
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
    def read(self, file_name, use_raw=False):
        '''Read the given file.
        
        Normally we apply the registered hooks to translate certain structures
        to higher level objects (e.g., RSM). It can be useful to suppress that
        in certain contexts (e.g., nitfinfofull reporting raw TRE fields),
        so you can specify use_raw=True to skip hooks.'''
        self.file_name = file_name
        with open(file_name, 'rb') as fh:
            self.file_header.read_from_file(fh)
            hook_obj = NitfFile.image_segment_hook_obj
            if(use_raw):
                hook_obj = [h for h in hook_obj if not h.mark_remove_for_raw()]
            self.image_segment = \
               [NitfImageSegment(header_size=self.file_header.lish[i],
                                 data_size=self.file_header.li[i],
                                 hook_obj = hook_obj,
                                 nitf_file = self) for i in
                range(self.file_header.numi)]
            self.graphic_segment = \
               [NitfGraphicSegment(header_size=self.file_header.lssh[i],
                                   data_size=self.file_header.ls[i],
                                   nitf_file = self) for i in
                range(self.file_header.nums)]
            hook_obj = NitfFile.text_segment_hook_obj
            if(use_raw):
                hook_obj = [h for h in hook_obj if not h.mark_remove_for_raw()]
            self.text_segment = \
               [NitfTextSegment(header_size=self.file_header.ltsh[i],
                                data_size=self.file_header.lt[i],
                                hook_obj = hook_obj,
                                nitf_file = self) for i in
                range(self.file_header.numt)]
            hook_obj = NitfFile.des_segment_hook_obj
            if(use_raw):
                hook_obj = [h for h in hook_obj if not h.mark_remove_for_raw()]
            self.des_segment = \
               [NitfDesSegment(header_size=self.file_header.ldsh[i],
                              data_size=self.file_header.ld[i],
                               hook_obj = hook_obj,
                               nitf_file = self) for i in
                range(self.file_header.numdes)]
            self.res_segment = \
               [NitfResSegment(header_size=self.file_header.lresh[i], 
                               data_size=self.file_header.lre[i],
                               nitf_file = self) for i in
                range(self.file_header.numres)]
            for seglist in [self.image_segment, self.graphic_segment, 
                            self.text_segment, self.des_segment, 
                            self.res_segment]:
                for i, seg in enumerate(seglist):
                    seg.read_from_file(fh, i)
            self.tre_list = read_tre(self.file_header, self.des_segment,
                                     [["xhdl", "xhdlofl", "xhd"],
                                      ["udhdl", "udhofl", "udhd"]])
            for seglist in [self.image_segment, self.graphic_segment, 
                            self.text_segment, self.des_segment, 
                            self.res_segment]:
                for seg in self.image_segment:
                    seg.read_tre(self.des_segment)

    def write(self, file_name):
        '''Write to the given file'''
        self.des_segment = [dseg for dseg in self.des_segment
                            if(dseg.subheader.desid.encode("utf-8") !=
                               b'TRE_OVERFLOW')]
        with open(file_name, 'wb') as fh:
            h = self.file_header
            prepare_tre_write(self.tre_list, h, self.des_segment,
                              [["xhdl", "xhdlofl", "xhd"],
                               ["udhdl", "udhofl", "udhd"]])
            for seglist in [self.image_segment, self.graphic_segment, 
                            self.text_segment, self.des_segment,
                            self.res_segment]:
                for i, seg in enumerate(seglist):
                    # Seg index is 1 based, so add 1 to get it
                    seg.prepare_tre_write(self.des_segment, i+1)
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
            for seglist, fhs, fds in [[self.image_segment, "lish", "li"],
                                      [self.graphic_segment, "lssh", "ls"],
                                      [self.text_segment, "ltsh", "lt"],
                                      [self.des_segment, "ldsh", "ld"],
                                      [self.res_segment, "lresh", "lre"]]:
                for i, seg in enumerate(seglist):
                    hs, ds = seg.write_to_file(fh)
                    h.update_field(fh, fhs, hs, (i,))
                    h.update_field(fh, fds, ds, (i,))
            # Now we have to update the file length
            h.update_field(fh, "fl", fh.tell())
        # Special handling for the TRE overflow DES. We create these as
        # needed for the TREs that we already have stored various places.
        # Clear out any that generated during our write
        self.des_segment = [dseg for dseg in self.des_segment
                            if(dseg.subheader.desid.encode("utf-8") !=
                               b'TRE_OVERFLOW')]
            
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

class NitfSegmentHook(object):
    '''To allow special handling of TREs etc. we allow a hook_list of
    these objects to be passed to NitfSegment. These then are called in
    each function of NitfSegment.

    Note that you don't need to strictly derive from this class, we use
    the standard "duck" typing of python. This is just the list of functions
    that need to be supplied.

    See for example geocal_nitf_rsm.py in geocal for an example of using
    these hooks to add in support for the geocal Rsm object.
    '''
    def init_hook(self, seg):
        '''Called at the end of NitfSegment.__init__'''
        pass
    def prepare_tre_write_hook(self, seg, des_list, seg_index):
        '''Called at the start of NitfSegment.prepare_tre_write'''
        pass
    def read_tre_hook(self, seg, des_list):
        '''Called at the end of NitfSegment.read_tre'''
        pass
    def str_hook(self, seg, fh):
        '''Called at the start of NitfSegment.__str__'''
        pass
    def mark_remove_for_raw(self):
        '''Hooks usually map to some higher level object (e.g., Geocal
        handling RSM. Normally you want this, but for certain contexts it
        can be useful to suppress this behavior, e.g., nitfinfofull reporting
        the raw TRE data rather than the objects generated by the TRE
        data.
        
        These hooks can be removed if we want to report the raw
        data. The hooks are by default marked as "True" for removing,
        but if you have some special case where you want to avoid
        removing the hook you can have the derived class change this
        to False.'''
        return True
    def str_tre_handle_hook(self, seg, tre, fh):
        '''Called before printing a TRE. If this returns true we assume
        that this class has handled the TRE printing. Otherwise, we
        call print on the tre'''
        return False
        
# Add engrda to give hash access to ENGRDA TREs
add_engrda_function(NitfFile)

# Add TRE finding functions
add_find_tre_function(NitfFile)
    
__all__ = ["NitfFile", "NitfSegmentHook", ]

           
           
