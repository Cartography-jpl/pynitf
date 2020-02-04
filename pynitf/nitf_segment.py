from .nitf_security import security_unclassified
from .nitf_tre_engrda import add_engrda_function
from .nitf_tre import read_tre, prepare_tre_write, add_find_tre_function
from .nitf_image_subheader import NitfImageSubheader
from .nitf_text_subheader import NitfTextSubheader
from .nitf_des_subheader import NitfDesSubheader
from .nitf_image import NitfImageHandleSet
from .nitf_des import NitfDesHandleSet
import io
import weakref
import copy

class NitfSegment(object):
    def __init__(self, subheader, data, nitf_file = None):
        self.subheader = subheader
        self.data = data
        # For simplicity, always have a tre_list. For types that don't have
        # TREs (NitfDesSegment and NitfResSegment) this is just an empty
        # list. But having this means we can avoid special handling.
        self.tre_list = []
        # Only keep a weak reference. We don't want to keep a NitfFile from
        # garbage collection just because a NitfSegment points back to it.
        if(nitf_file is not None):
            self._nitf_file = weakref.ref(nitf_file)
        else:
            self._nitf_file = None
        if(self.nitf_file):
            self.nitf_file.segment_hook_set.after_init_hook(self,
                                                            self.nitf_file)
    @property
    def nitf_file(self):
        if(self._nitf_file is None):
            return None
        return self._nitf_file()


    @property
    def security(self):
        '''NitfSecurity for Segment.'''
        return self.subheader.security

    @security.setter
    def security(self, v):
        '''Set NitfSecurity for Segment.'''
        self.subheader.security = v
        
    def type_support_tre(self):
        '''True if this is a type that supports TREs, i.e., it is a 
        NitfImageSegment, NitfTextSegment or NitfGraphicSegment.'''
        return False

    def __str__(self):
        '''Text description of structure, e.g., something you can print out'''
        fh = io.StringIO()
        if(self.nitf_file):
            self.nitf_file.segment_hook_set.before_str_hook(self,
                                                            self.nitf_file, fh)
        print("Sub header:", file=fh)
        print(self.subheader, file=fh)
        if(self.type_support_tre()):
            print("TREs:", file=fh)
            if(len(self.tre_list) == 0):
                print("No segment level TREs", file=fh)
            else:
                for tre in self.tre_list:
                    was_processed = self.nitf_file.segment_hook_set.before_str_tre_hook(self, tre, self.nitf_file, fh)
                    if(not was_processed):
                        print(tre, file=fh)
        print("Data", file=fh)
        print(self.data, file=fh)
        return fh.getvalue()

    def summary(self):
        res = io.StringIO()
        print("Segment level TRES:", file=res)
        if (hasattr(self, 'tre_list') == True):
            for t in self.tre_list:
                print(t.summary(), file=res, end='', flush=True)

        return self.subheader.summary() + res.getvalue()

    def read_tre(self, des_list):
        '''Read the TREs in a segment.'''
        # By default, segment doesn't have any TREs
        pass

    def prepare_tre_write(self, seg_index, des_list):
        '''Process the TREs in a segment putting them in the various places
        in header and DES overflow before writing out the segment.

        The seg_index should be the normal 0 based index used in python for
        lists. We internally translate this too and from the 1 based indexing
        used in the NITF file.'''
        # By default, segment doesn't have any TREs
        pass
    
    def read_from_file(self, fh, segindex=None):
        '''Read from a file. Note that we pass in the 0 based segment index 
        number. Most readers don't care at all about this, but it can be
        useful for implementing some external code readers (e.g., GDAL
        can read an image segment by the file name and index)'''
        self.subheader.read_from_file(fh)
        self.data.read_from_file(fh)

    def _update_file_header(self, fh, nitf_file, seg_index, sz_header, sz_data):
        '''Update the NITF file header with the segment header and data size.'''
        pass

    def write_to_file(self, fh, seg_index, nitf_file):
        '''Write to a file. We also update the file header information in 
        the nitf_file passed in with the header and data size for this segment.
        
        The nitf_file can be passed as None to skip the file header update. 
        This isn't generally used in real code, but it can be useful for unit
        tests (so testing a segment writing w/o needing a full NitfFile in the
        test).'''
        start_pos = fh.tell()
        self.subheader.write_to_file(fh)
        sz_header = fh.tell() - start_pos
        start_pos = fh.tell()
        self.data.write_to_file(fh)
        sz_data = fh.tell() - start_pos
        # Normally nitf_file will be present, but for unit tests it
        # can be useful to skip this
        if(nitf_file):
            self._update_file_header(fh, nitf_file, seg_index, sz_header,
                                    sz_data)
        # Return value not normally needed, but can be useful for unit
        # tests.
        return (sz_header, sz_data)

class NitfPlaceHolder(NitfSegment):
    '''Implementation of NitfSegment that just skips over the data.'''
    def __init__(self, header_size, data_size, type_name, nitf_file=None):
        NitfSegment.__init__(self, None, None, nitf_file = nitf_file)
        self.sz = header_size + data_size
        self.type_name = type_name
        self.seg_start = None
        
    def __str__(self):
        '''Text description of structure, e.g., something you can print out'''
        fh = io.StringIO()
        print("%s segment, size %d" % (self.type_name, self.sz), file=fh)
        return fh.getvalue()

    def read_from_file(self, fh, segindex=None):
        '''Read from a file'''
        # Just skip over the data
        self.seg_start = fh.tell()
        fh.seek(self.sz, 1)

    def write_to_file(self, fh, seg_index, nitf_file):
        '''Write to a file. The returns (sz_header, sz_data), because this
        information is needed by NitfFile.'''
        raise NotImplementedError("write_to_file not implemented for %s" % self.type_name)

class NitfImageSegment(NitfSegment):
    '''Image segment (IS), supports the standard image type of data.
    '''
    def __init__(self, image = None,
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
        NitfSegment.__init__(self, h, image, nitf_file = nitf_file)
        # Override security already set in NitfImage if desired.
        if(security is not None):
            self.security = security
            
    def read_from_file(self, fh, segindex=None):
        '''Read from a file'''
        self.subheader.read_from_file(fh)
        ihs = self.nitf_file.image_handle_set if self.nitf_file else NitfImageHandleSet.default_handle_set()
        self.data = ihs.handle(self.subheader, self.header_size,
                               self.data_size, fh, segindex)
    def prepare_tre_write(self, seg_index, des_list):
        '''Process the TREs in a segment putting them in the various places
        in header and DES overflow before writing out the segment.

        The seg_index should be the normal 0 based index used in python for
        lists. We internally translate this too and from the 1 based indexing
        used in the NITF file.'''
        prepare_tre_write(self.tre_list, self.subheader,des_list,
                          [["ixshdl", "ixofl", "ixshd"],
                           ["udidl", "udofl", "udid"]], seg_index)
    def read_tre(self, des_list):
        self.tre_list = read_tre(self.subheader,des_list,
                                 [["ixshdl", "ixofl", "ixshd"],
                                  ["udidl", "udofl", "udid"]])

    def type_support_tre(self):
        '''True if this is a type that supports TREs, i.e., it is a 
        NitfImageSegment, NitfTextSegment or NitfGraphicSegment.'''
        return True

    def _update_file_header(self, fh, nitf_file, seg_index, sz_header, sz_data):
        '''Update the NITF file header with the segment header and data size.'''
        nitf_file.file_header.update_field(fh, "lish", sz_header, (seg_index,))
        nitf_file.file_header.update_field(fh, "li", sz_data, (seg_index,))

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
    def __init__(self, header_size=None, data_size=None, nitf_file=None):
        NitfPlaceHolder.__init__(self, header_size, data_size,
                                 "Graphic Segment", nitf_file=nitf_file)
    def prepare_tre_write(self, seg_index, des_list):
        '''Process the TREs in a segment putting them in the various places
        in header and DES overflow before writing out the segment.

        The seg_index should be the normal 0 based index used in python for
        lists. We internally translate this too and from the 1 based indexing
        used in the NITF file.'''
        prepare_tre_write(self.tre_list, self.subheader,des_list,
                          [["sxshdl", "sxsofl", "sxshd"]], seg_index)
    def read_tre(self, des_list):
        self.tre_list = read_tre(self.subheader,des_list,
                                 [["sxshdl", "sxsofl", "sxshd"]])

    def _update_file_header(self, fh, nitf_file, seg_index, sz_header, sz_data):
        '''Update the NITF file header with the segment header and data size.'''
        nitf_file.file_header.update_field(fh, "lssh", sz_header, (seg_index,))
        nitf_file.file_header.update_field(fh, "ls", sz_data, (seg_index,))

    def type_support_tre(self):
        '''True if this is a type that supports TREs, i.e., it is a 
        NitfImageSegment, NitfTextSegment or NitfGraphicSegment.'''
        return True


class NitfTextSegment(NitfSegment):
    '''Text segment (TS), support the standard text type of data. 
    Note that txt can be either a str or bytes, whichever is most convenient
    for you. We encode/decode using utf-8 as needed. You can access the data
    as one or the other using data_as_bytes and data_as_str.'''
    def __init__(self, txt='', header_size=None, data_size=None,
                 nitf_file=None,
                 security=security_unclassified):
        h = NitfTextSubheader()
        self.header_size = header_size
        self.data_size = data_size
        NitfSegment.__init__(self, h, copy.copy(txt), nitf_file = nitf_file)
        self.tre_list = []
        self.security = security
        
    def read_from_file(self, fh, segindex=None):
        '''Read from a file'''
        self.subheader.read_from_file(fh)
        self.data = fh.read(self.data_size)

    def prepare_tre_write(self, seg_index, des_list):
        '''Process the TREs in a segment putting them in the various places
        in header and DES overflow before writing out the segment.

        The seg_index should be the normal 0 based index used in python for
        lists. We internally translate this too and from the 1 based indexing
        used in the NITF file.'''
        prepare_tre_write(self.tre_list, self.subheader,des_list,
                          [["txshdl", "txsofl", "txshd"]], seg_index)
    def read_tre(self, des_list):
        self.tre_list = read_tre(self.subheader,des_list,
                                 [["txshdl", "txsofl", "txshd"]])

    @property
    def data_as_bytes(self):
        '''Return data as bytes, encoding if needed'''
        if isinstance(self.data, str):
            return self.data.encode('utf-8')
        return self.data
            
    @property
    def data_as_str(self):
        '''Return data as str, encoding if needed'''
        if isinstance(self.data, str):
            return self.data
        return self.data.decode('utf-8')

    def write_to_file(self, fh, seg_index, nitf_file):
        '''Write to a file. The returns (sz_header, sz_data), because this
        information is needed by NitfFile.'''
        # TODO Can likely replace this with the NitfSegment version.
        start_pos = fh.tell()
        self.subheader.write_to_file(fh)
        sz_header = fh.tell() - start_pos
        start_pos = fh.tell()
        fh.write(self.data_as_bytes)
        sz_data = fh.tell() - start_pos
        if(nitf_file):
            self._update_file_header(fh, nitf_file, seg_index, sz_header,
                                    sz_data)
        return (sz_header, sz_data)

    def type_support_tre(self):
        '''True if this is a type that supports TREs, i.e., it is a 
        NitfImageSegment, NitfTextSegment or NitfGraphicSegment.'''
        return True

    def _update_file_header(self, fh, nitf_file, seg_index, sz_header, sz_data):
        '''Update the NITF file header with the segment header and data size.'''
        nitf_file.file_header.update_field(fh, "ltsh", sz_header, (seg_index,))
        nitf_file.file_header.update_field(fh, "lt", sz_data, (seg_index,))

    
class NitfDesSegment(NitfSegment):
    '''Data extension segment (DES), allows for the addition of different data 
    types with each type encapsulated in its own DES'''
    def __init__(self, des=None,
                 header_size=None, data_size=None, nitf_file = None):
        if(des is None):
            h = NitfDesSubheader()
        else:
            h = des.des_subheader
        self.header_size = header_size
        self.data_size = data_size
        NitfSegment.__init__(self, h, des, nitf_file = nitf_file)

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
        # Special case for TRE_OVERFLOW
        # Because we will print the data out as TREs later so we'll skip
        # printing here
        if(self.subheader.desid.encode("utf-8") == b'TRE_OVERFLOW'):
            return ""
        return super().__str__()

    def write_to_file(self, fh, seg_index, nitf_file):
        '''Write to a file. The returns (sz_header, sz_data), because this
        information is needed by NitfFile.'''
        # TODO Can likely replace this with the NitfSegment version.
        start_pos = fh.tell()
        self.des.write_user_subheader(self.subheader)
        self.subheader.write_to_file(fh)
        sz_header = fh.tell() - start_pos
        start_pos = fh.tell()
        self.des.write_to_file(fh)
        sz_data = fh.tell() - start_pos
        if(nitf_file):
            self._update_file_header(fh, nitf_file, seg_index, sz_header,
                                    sz_data)
        return (sz_header, sz_data)

    def _update_file_header(self, fh, nitf_file, seg_index, sz_header, sz_data):
        '''Update the NITF file header with the segment header and data size.'''
        nitf_file.file_header.update_field(fh, "ldsh", sz_header, (seg_index,))
        nitf_file.file_header.update_field(fh, "ld", sz_data, (seg_index,))
    

class NitfResSegment(NitfPlaceHolder):
    '''Reserved extension segment (RES), non-standard data segment which is
    user-defined. A NITF file can support different user-defined types of 
    segments called RES.'''
    def __init__(self, header_size=None, data_size=None, nitf_file=None):
        NitfPlaceHolder.__init__(self, header_size, data_size, "RES",
                                 nitf_file=nitf_file)
        
    def _update_file_header(self, fh, nitf_file, seg_index, sz_header, sz_data):
        '''Update the NITF file header with the segment header and data size.'''
        nitf_file.file_header.update_field(fh, "lresh", sz_header, (seg_index,))
        nitf_file.file_header.update_field(fh, "lre", sz_data, (seg_index,))


# Add engrda to give hash access to ENGRDA TREs
add_engrda_function(NitfSegment)

# Add TRE finding functions
add_find_tre_function(NitfSegment)

__all__ = ["NitfSegment",
           "NitfPlaceHolder", "NitfImageSegment", "NitfGraphicSegment",
           "NitfTextSegment", "NitfDesSegment", "NitfResSegment",
           ]
