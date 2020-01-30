from .nitf_security import security_unclassified
from .nitf_tre_engrda import add_engrda_function
from .nitf_tre import read_tre, prepare_tre_write, add_find_tre_function
from .nitf_image_subheader import NitfImageSubheader
from .nitf_text_subheader import NitfTextSubheader
from .nitf_des_subheader import NitfDesSubheader
from .nitf_image import NitfImageHandleSet
from .nitf_des import NitfDesHandleSet
import six
import weakref
import copy

class NitfSegment(object):
    def __init__(self, subheader, data, nitf_file = None, hook_obj = []):
        self.subheader = subheader
        self.data = data
        self.hook_obj = hook_obj
        # Only keep a weak reference. We don't want to keep a NitfFile from
        # garbage collection just because a NitfSegment points back to it.
        if(nitf_file is not None):
            self._nitf_file = weakref.ref(nitf_file)
        else:
            self._nitf_file = None
        for ho in self.hook_obj:
            ho.init_hook(self)

    @property
    def nitf_file(self):
        if(self._nitf_file is None):
            return None
        return self._nitf_file()

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
    
    def read_from_file(self, fh, segindex=None):
        '''Read from a file. Note that we pass in the 0 based segment index 
        number. Most readers don't care at all about this, but it can be
        useful for implementing some external code readers (e.g., GDAL
        can read an image segment by the file name and index)'''
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
    def __init__(self, header_size, data_size, type_name, nitf_file=None):
        NitfSegment.__init__(self, None, None, nitf_file = nitf_file)
        self.sz = header_size + data_size
        self.type_name = type_name
        self.seg_start = None
        
    def __str__(self):
        '''Text description of structure, e.g., something you can print out'''
        fh = six.StringIO()
        print("%s segment, size %d" % (self.type_name, self.sz), file=fh)
        return fh.getvalue()

    def read_from_file(self, fh, segindex=None):
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
                 header_size = None, data_size = None, nitf_file=None,
                 security = None):
        '''Initialize. You can pass a NitfImage class to use (i.e., you've
        created this for writing), or a list of classes to use to try
        to read an image. This list is tried in order, the first class
        that can handle an image is the one used.'''
        self.header_size = header_size
        self.data_size = data_size
        if(image is None):
            h = NitfImageSubheader()
        else:
            h = image.image_subheader
        self.tre_list = []
        if(hook_obj is None):
            from .nitf_file import NitfFile
            hook_obj = NitfFile.image_segment_hook_obj
        NitfSegment.__init__(self, h, image, hook_obj = hook_obj,
                             nitf_file = nitf_file)
        # Override security already set in NitfImage if desired.
        if(security is not None):
            self.security = security
            
    def read_from_file(self, fh, segindex=None):
        '''Read from a file'''
        self.subheader.read_from_file(fh)
        ihs = self.nitf_file.image_handle_set if self.nitf_file else NitfImageHandleSet.default_handle_set()
        self.data = ihs.handle(self.subheader, self.header_size,
                               self.data_size, fh, segindex)
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

    @property
    def security(self):
        '''NitfSecurity for Image.'''
        return self.subheader.security

    @security.setter
    def security(self, v):
        '''Set NitfSecurity for Image.'''
        self.subheader.security = v

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

    # Few properties from image_subheader that we want at this level
    @property
    def idlvl(self):
        return self.subheader.idlvl

    @idlvl.setter
    def idlvl(self, lvl):
        self.subheader.idlvl = lvl

    @property
    def iid1(self):
        return self.subheader.iid1

    @iid1.setter
    def iid1(self, v):
        self.subheader.iid1 = v
    
    
class NitfGraphicSegment(NitfPlaceHolder):
    '''Graphic segment (GS), support the standard graphic type of data.'''
    def __init__(self, header_size=None, data_size=None, nitf_file=None,
                 hook_obj = []):
        NitfPlaceHolder.__init__(self, header_size, data_size,
                                 "Graphic Segment", nitf_file=nitf_file,
                                 hook_obj=hook_obj)

class NitfTextSegment(NitfSegment):
    '''Text segment (TS), support the standard text type of data. 
    Note that txt can be either a str or bytes, whichever is most convenient
    for you. We encode/decode using utf-8 as needed. You can access the data
    as one or the other using data_as_bytes and data_as_str.'''
    def __init__(self, txt='', header_size=None, data_size=None,
                 hook_obj = None, nitf_file=None,
                 security=security_unclassified):
        h = NitfTextSubheader()
        self.header_size = header_size
        self.data_size = data_size
        if(hook_obj is None):
            from .nitf_file import NitfFile
            hook_obj = NitfFile.image_segment_hook_obj
        NitfSegment.__init__(self, h, copy.copy(txt), hook_obj = hook_obj,
                             nitf_file = nitf_file)
        self.tre_list = []
        self.security = security
        
    def read_from_file(self, fh, segindex=None):
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

    @property
    def security(self):
        '''NitfSecurity for Text.'''
        return self.subheader.security

    @security.setter
    def security(self, v):
        '''Set NitfSecurity for Text.'''
        self.subheader.security = v

    
class NitfDesSegment(NitfSegment):
    '''Data extension segment (DES), allows for the addition of different data 
    types with each type encapsulated in its own DES'''
    def __init__(self, des=None,
                 hook_obj = None,
                 header_size=None, data_size=None, nitf_file = None):
        if(des is None):
            h = NitfDesSubheader()
        else:
            h = des.des_subheader
        self.header_size = header_size
        self.data_size = data_size
        if(hook_obj is None):
            from .nitf_file import NitfFile
            hook_obj = NitfFile.des_segment_hook_obj
        NitfSegment.__init__(self, h, des, hook_obj = hook_obj,
                             nitf_file = nitf_file)

    @property
    def security(self):
        '''NitfSecurity for DES.'''
        return self.subheader.security

    @security.setter
    def security(self, v):
        '''Set NitfSecurity for DES.'''
        self.subheader.security = v
        
    # Alternative name for data, the des is stored in data attribute
    @property
    def des(self):
        return self.data

    def read_from_file(self, fh, segindex=None):
        '''Read from a file'''
        self.subheader.read_from_file(fh)
        dhs = self.nitf_file.des_handle_set if self.nitf_file else NitfDesHandleSet.default_handle_set()
        self.data = dhs.handle(self.subheader, self.header_size,
                               self.data_size, fh)
        
    def __str__(self):
        '''Text description of structure, e.g., something you can print out'''
        fh = six.StringIO()
        print("Sub header:", file=fh)
        print(self.subheader, file=fh)

        #Special case for TRE_OVERFLOW
        #Because we will print the data out as TREs later so we'll skip
        if (self.subheader.desid.encode("utf-8") == b'TRE_OVERFLOW'):
            return ""

        print(self.des, file=fh)

        return fh.getvalue()

    def write_to_file(self, fh):
        '''Write to a file. The returns (sz_header, sz_data), because this
        information is needed by NitfFile.'''
        start_pos = fh.tell()
        self.des.write_user_subheader(self.subheader)
        self.subheader.write_to_file(fh)
        header_pos = fh.tell()
        self.des.write_to_file(fh)
        return (header_pos - start_pos, fh.tell() - header_pos)

class NitfResSegment(NitfPlaceHolder):
    '''Reserved extension segment (RES), non-standard data segment which is
    user-defined. A NITF file can support different user-defined types of 
    segments called RES.'''
    def __init__(self, header_size=None, data_size=None, nitf_file=None,
                 hook_obj = []):
        NitfPlaceHolder.__init__(self, header_size, data_size, "RES",
                                 nitf_file=nitf_file, hook_obj=hook_obj)


# Add engrda to give hash access to ENGRDA TREs
add_engrda_function(NitfImageSegment)
add_engrda_function(NitfTextSegment)
add_engrda_function(NitfGraphicSegment)

# Add TRE finding functions
add_find_tre_function(NitfImageSegment)
add_find_tre_function(NitfTextSegment)
add_find_tre_function(NitfGraphicSegment)

__all__ = ["NitfSegment",
           "NitfPlaceHolder", "NitfImageSegment", "NitfGraphicSegment",
           "NitfTextSegment", "NitfDesSegment", "NitfResSegment",
           ]
