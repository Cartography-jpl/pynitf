# This contains the top level object for reading and writing a NITF file.
#
# The class structure is a little complicated, so you can look and the UML
# file doc/Nitf_file.xmi (e.g., use umbrello) to see the design.

from __future__ import print_function
from .nitf_file_header import NitfFileHeader
from .nitf_image_subheader import NitfImageSubheader
from .nitf_text_subheader import NitfTextSubheader
from .nitf_des_subheader import NitfDesSubheader
from .nitf_image import NitfImageFromNumpy, NitfImagePlaceHolder, \
    NitfImageGeneral, NitfImageCannotHandle
from .nitf_tre import read_tre, prepare_tre_write
import io,six,copy

class NitfFile(object):
    # List of hook objects to extend the handling in the various types of
    # segments. Right now we only do this for image_segment and text_segment,
    # but we could extend this if desired
    image_segment_hook_obj = []
    text_segment_hook_obj = []
    def __init__(self, file_name = None):
        '''Create a NitfFile for reading or writing. Because it is common, if
        you give a file_name we read from that file to populate the Nitf 
        structure. Otherwise we start with a default file (a file header, but
        no segments) - which you can then populate before calling write'''
        self.file_header = NitfFileHeader()
        # This is the order things appear in the file
        self.image_segment = []
        self.graphic_segment = []
        self.text_segment = []
        self.des_segment = []
        self.res_segment = []
        # These are the file level TREs. There can also be TREs at the
        # image segment level
        self.tre_list = []
        if(file_name is not None):
            self.read(file_name)
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
        print("NITF File Summary")
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
        '''Read the given file'''
        with open(file_name, 'rb') as fh:
            self.file_header.read_from_file(fh)
            self.image_segment = \
               [NitfImageSegment(header_size=self.file_header.lish[i],
                                 data_size=self.file_header.li[i],
                          hook_obj = NitfFile.image_segment_hook_obj) for i in
                range(self.file_header.numi)]
            self.graphic_segment = \
               [NitfGraphicSegment(header_size=self.file_header.lssh[i],
                                   data_size=self.file_header.ls[i]) for i in
                range(self.file_header.nums)]
            self.text_segment = \
               [NitfTextSegment(header_size=self.file_header.ltsh[i],
                                data_size=self.file_header.lt[i],
                         hook_obj = NitfFile.text_segment_hook_obj) for i in
                range(self.file_header.numt)]
            self.des_segment = \
               [NitfDesSegment(header_size=self.file_header.ldsh[i],
                               data_size=self.file_header.ld[i]) for i in
                range(self.file_header.numdes)]
            self.res_segment = \
               [NitfResSegment(header_size=self.file_header.lresh[i], 
                               data_size=self.file_header.lre[i]) for i in
                range(self.file_header.numres)]
            for seglist in [self.image_segment, self.graphic_segment, 
                            self.text_segment, self.des_segment, 
                            self.res_segment]:
                for seg in seglist:
                    seg.read_from_file(fh)
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
    def str_tre_handle_hook(self, seg, tre, fh):
        '''Called before printing a TRE. If this returns true we assume
        that this class has handled the TRE printing. Otherwise, we
        call print on the tre'''
        return False
        
class NitfSegment(object):
    def __init__(self, subheader, data, hook_obj = []):
        self.subheader = subheader
        self.data = data
        self.hook_obj = hook_obj
        for ho in self.hook_obj:
            ho.init_hook(self)

    def __str__(self):
        '''Text description of structure, e.g., something you can print out'''
        fh = six.StringIO()
        for ho in self.hook_obj:
            ho.str_hook(self, fh)
        print("Sub header:", file=fh)
        print(self.subheader, file=fh)
        print("Data", file=fh)
        print(self.data, file=fh)
        return fh.getvalue()

    def summary(self):
        res = six.StringIO()
        print("Segment level TRES:", file=res)
        if (hasattr(self, 'tre_list') == True):
            for t in self.tre_list:
                print(t.summary(), file=res, end='', flush=True)

        return self.subheader.summary() + res.getvalue()

    def read_tre(self, des_list):
        # By default, segment doesn't have any TREs
        #pass
        for ho in self.hook_obj:
            ho.read_tre_hook(self, des_list)

    def prepare_tre_write(self, des_list, seg_index):
        '''Process the TREs in a segment putting them in the various places
        in header and DES overflow before writing out the segment.'''
        for ho in self.hook_obj:
            ho.prepare_tre_write_hook(self, des_list, seg_index)
        # By default, segment doesn't have any TREs
        pass
    
    def read_from_file(self, fh):
        '''Read from a file'''
        self.subheader.read_from_file(fh)
        self.data.read_from_file(fh)

    def write_to_file(self, fh):
        '''Write to a file. The returns (sz_header, sz_data), because this
        information is needed by NitfFile.'''
        start_pos = fh.tell()
        self.subheader.write_to_file(fh)
        header_pos = fh.tell()
        self.data.write_to_file(fh)
        return (header_pos - start_pos, fh.tell() - header_pos)

class NitfPlaceHolder(NitfSegment):
    '''Implementation of NitfSegment that just skips over the data.'''
    def __init__(self, header_size, data_size, type_name):
        NitfSegment.__init__(self, None, None)
        self.sz = header_size + data_size
        self.type_name = type_name
        self.seg_start = None
        
    def __str__(self):
        '''Text description of structure, e.g., something you can print out'''
        fh = six.StringIO()
        print("%s segment, size %d" % (self.type_name, self.sz), file=fh)
        return fh.getvalue()

    def read_from_file(self, fh):
        '''Read from a file'''
        # Just skip over the data
        self.seg_start = fh.tell()
        fh.seek(self.sz, 1)

    def write_to_file(self, fh):
        '''Write to a file. The returns (sz_header, sz_data), because this
        information is needed by NitfFile.'''
        raise NotImplementedError("write_to_file not implemented for %s" % self.type_name)

class NitfImageSegment(NitfSegment):
    '''Image segment (IS), supports the standard image type of data.
    
    To support adding special handling of TREs etc we allow 
    hook_obj to contain hook objects that are called at various places in
    the code. See for example geocal_nitf_rsm.py in geocal for an example
    of this.
    '''
    def __init__(self, image = None,
                 hook_obj = None,
                 header_size = None, data_size = None,
                 nitf_image_handle = [NitfImageFromNumpy,
                                      NitfImageGeneral,
                                      NitfImagePlaceHolder]):
        '''Initialize. You can pass a NitfImage class to use (i.e., you've
        created this for writing), or a list of classes to use to try
        to read an image. This list is tried in order, the first class
        that can handle an image is the one used.'''
        self.header_size = header_size
        self.data_size = data_size
        self.nitf_image_handle = nitf_image_handle
        if(image is None):
            h = NitfImageSubheader()
        else:
            h = image.image_subheader
        self.tre_list = []
        if(hook_obj is None):
            hook_obj = NitfFile.image_segment_hook_obj
        NitfSegment.__init__(self, h, image, hook_obj = hook_obj)
    def read_from_file(self, fh):
        '''Read from a file'''
        self.subheader.read_from_file(fh)
        for i,cls in enumerate(self.nitf_image_handle):
            t = cls(image_subheader=self.subheader,
                    header_size=self.header_size,
                    data_size=self.data_size)
            try:
                t.read_from_file(fh)
                break
            except NitfImageCannotHandle:
                if(i < len(self.nitf_image_handle) - 1):
                    pass
                else:
                    raise
        self.data = t
    def prepare_tre_write(self, des_list, seg_index):
        for ho in self.hook_obj:
            ho.prepare_tre_write_hook(self, des_list, seg_index)
        prepare_tre_write(self.tre_list, self.subheader,des_list,
                          [["ixshdl", "ixofl", "ixshd"],
                           ["udidl", "udofl", "udid"]], seg_index)
    def read_tre(self, des_list):
        self.tre_list = read_tre(self.subheader,des_list,
                                 [["ixshdl", "ixofl", "ixshd"],
                                  ["udidl", "udofl", "udid"]])
        for ho in self.hook_obj:
            ho.read_tre_hook(self, des_list)

    def __str__(self):
        '''Text description of structure, e.g., something you can print out'''
        fh = six.StringIO()
        for ho in self.hook_obj:
            ho.str_hook(self, fh)
        print("Sub header:", file=fh)
        print(self.subheader, file=fh)
        print("TREs:", file=fh)
        if(len(self.tre_list) == 0):
            print("No image level TREs", file=fh)
        else:
            for tre in self.tre_list:
                was_processed = False
                for ho in self.hook_obj:
                    if(not was_processed):
                        was_processed = ho.str_tre_handle_hook(self, tre, fh)
                if(not was_processed):
                    print(tre, file=fh)
        print("Data", file=fh)
        print(self.data, file=fh)
        return fh.getvalue()

class NitfGraphicSegment(NitfPlaceHolder):
    '''Graphic segment (GS), support the standard graphic type of data.'''
    def __init__(self, header_size=None, data_size=None):
        NitfPlaceHolder.__init__(self, header_size, data_size, "Graphic Segment")

class NitfTextSegment(NitfSegment):
    '''Text segment (TS), support the standard text type of data. 
    Note that txt can be either a str or bytes, whichever is most convenient
    for you. We encode/decode using utf-8 as needed. You can access the data
    as one or the other using data_as_bytes and data_as_str.'''
    def __init__(self, txt='', header_size=None, data_size=None,
                 hook_obj = None):
        h = NitfTextSubheader()
        self.header_size = header_size
        self.data_size = data_size
        if(hook_obj is None):
            hook_obj = NitfFile.image_segment_hook_obj
        NitfSegment.__init__(self, h, copy.copy(txt), hook_obj = hook_obj)
        self.tre_list = []
    def read_from_file(self, fh):
        '''Read from a file'''
        self.subheader.read_from_file(fh)
        self.data = fh.read(self.data_size)

    def prepare_tre_write(self, des_list, seg_index):
        for ho in self.hook_obj:
            ho.prepare_tre_write_hook(self, des_list, seg_index)
        prepare_tre_write(self.tre_list, self.subheader,des_list,
                          [["txshdl", "txsofl", "txshd"]], seg_index)
    def read_tre(self, des_list):
        self.tre_list = read_tre(self.subheader,des_list,
                                 [["txshdl", "txsofl", "txshd"]])
        for ho in self.hook_obj:
            ho.read_tre_hook(self, des_list)

    @property
    def data_as_bytes(self):
        '''Return data as bytes, encoding if needed'''
        if isinstance(self.data, six.string_types):
            return self.data.encode('utf-8')
        return self.data
            
    @property
    def data_as_str(self):
        '''Return data as str, encoding if needed'''
        if isinstance(self.data, six.string_types):
            return self.data
        return self.data.decode('utf-8')

    def __str__(self):
        '''Text description of structure, e.g., something you can print out'''
        fh = six.StringIO()
        for ho in self.hook_obj:
            ho.str_hook(self, fh)
        print("Sub header:", file=fh)
        print(self.subheader, file=fh)
        print("TREs:", file=fh)
        if(len(self.tre_list) == 0):
            print("No text level TREs", file=fh)
        else:
            for tre in self.tre_list:
                was_processed = False
                for ho in self.hook_obj:
                    if(not was_processed):
                        was_processed = ho.str_tre_handle_hook(self, tre, fh)
                if(not was_processed):
                    print(tre, file=fh)
        print("Text", file=fh)
        print(self.data_as_str, file=fh)
        return fh.getvalue()
    def write_to_file(self, fh):
        '''Write to a file. The returns (sz_header, sz_data), because this
        information is needed by NitfFile.'''
        start_pos = fh.tell()
        self.subheader.write_to_file(fh)
        header_pos = fh.tell()
        fh.write(self.data_as_bytes)
        return (header_pos - start_pos, fh.tell() - header_pos)
   
class NitfDesSegment(NitfSegment):
    '''Data extension segment (DES), allows for the addition of different data 
    types with each type encapsulated in its own DES'''
    def __init__(self, data='', header_size=None, data_size=None):
        h = NitfDesSubheader()
        self.header_size = header_size
        self.data_size = data_size
        NitfSegment.__init__(self, h, copy.copy(data))
    def read_from_file(self, fh):
        '''Read from a file'''
        self.subheader.read_from_file(fh)
        self.data = fh.read(self.data_size)
    def __str__(self):
        '''Text description of structure, e.g., something you can print out'''
        fh = six.StringIO()
        print("Sub header:", file=fh)
        print(self.subheader, file=fh)
        print("Data length %d" % len(self.data), file=fh)
        return fh.getvalue()
    def write_to_file(self, fh):
        '''Write to a file. The returns (sz_header, sz_data), because this
        information is needed by NitfFile.'''
        start_pos = fh.tell()
        self.subheader.write_to_file(fh)
        header_pos = fh.tell()
        fh.write(self.data)
        return (header_pos - start_pos, fh.tell() - header_pos)

class NitfResSegment(NitfPlaceHolder):
    '''Reserved extension segment (RES), non-standard data segment which is
    user-defined. A NITF file can support different user-defined types of 
    segments called RES.'''
    def __init__(self, header_size=None, data_size=None):
        NitfPlaceHolder.__init__(self, header_size, data_size, "RES")

__all__ = ["NitfFile", "NitfSegmentHook", "NitfSegment",
           "NitfPlaceHolder", "NitfImageSegment", "NitfGraphicSegment",
           "NitfTextSegment", "NitfDesSegment", "NitfResSegment"]

           
           
