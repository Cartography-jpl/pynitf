from .nitf_security import security_unclassified
from .nitf_tre_engrda import add_engrda_function
from .nitf_tre import read_tre, prepare_tre_write, add_find_tre_function
from .nitf_image_subheader import NitfImageSubheader
from .nitf_text_subheader import NitfTextSubheader
from .nitf_des_subheader import NitfDesSubheader
from .nitf_graphic_subheader import NitfGraphicSubheader
from .nitf_res_subheader import NitfResSubheader
import io
import weakref
import copy

class NitfSharedHeader(object):
    '''Both NitfData and NitfSegment need access to the subheader and
    user_subheader of a segment. In some sense the NitfSegment "owns" this
    since it is responsible for reading and writing the data. But often a
    NitfData is created first. So we have a small object to hold this data,
    and this object gets shared between the two. This is an implementation
    detail, it shouldn't make any difference outside of these classes - the
    subheader and user_subheader just "do the right thing" when shared between
    the two.'''
    def __init__(self, sh_class, uh_class):
        self.subheader = sh_class()
        if(uh_class):
            self.user_subheader = uh_class()
        else:
            self.user_subheader = None
        
class NitfSegment(object):
    sh_class = None
    _update_file_header_field = (None, None)
    _type_support_tre = False
    _tre_field_list = None
    def __init__(self, data=None, header_size=None, data_size=None,
                 nitf_file = None, security = None):
        self.data = data
        if(self.data):
            self._shared_header = data._shared_header
        else:
            self._shared_header = NitfSharedHeader(self.sh_class, None)
        self.header_size = header_size
        self.data_size = data_size
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
        # Override security already set subheader if desired.
        if(security is not None):
            self.security = security
        if(self.nitf_file):
            self.nitf_file.segment_hook_set.after_init_hook(self,
                                                            self.nitf_file)

    def short_desc(self):
        pass

    @property
    def subheader(self):
        '''Return subheader for NitfSegment'''
        return self._shared_header.subheader

    @subheader.setter
    def subheader(self, v):
        '''Set subheader for NitfSegment'''
        self._shared_header.subheader = v
    
    @property
    def user_subheader(self):
        '''Return user_subheader for NitfSegment'''
        return self._shared_header.user_subheader

    @user_subheader.setter
    def user_subheader(self, v):
        '''Set user_subheader for NitfSegment'''
        self._shared_header.user_subheader = v
    
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
        
    def __str__(self):
        '''Text description of structure, e.g., something you can print out'''
        fh = io.StringIO()
        if(self.nitf_file):
            self.nitf_file.segment_hook_set.before_str_hook(self,
                                                            self.nitf_file, fh)
        print("Sub header:", file=fh)
        print(self.subheader, file=fh)
        if(self.user_subheader):
            print("User-Defined Subheader: ", file=fh)
            print(self.user_subheader, file=fh)
        if(self._type_support_tre):
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
        if (hasattr(self, 'tre_list') == True and
            len(self.tre_list) > 0):
            print("Segment level TRES:", file=res)
            for t in self.tre_list:
                print(t.summary(), file=res, end='', flush=True)
        else:
            print("No Segment level TRES", file=res)
                
        return self.subheader.summary() + res.getvalue()

    def read_tre(self, des_list):
        '''Read the TREs in a segment.'''
        if(self._type_support_tre):
            self.tre_list = read_tre(self.subheader,des_list,
                                     self._tre_field_list)

    def prepare_tre_write(self, seg_index, des_list):
        '''Process the TREs in a segment putting them in the various places
        in header and DES overflow before writing out the segment.

        The seg_index should be the normal 0 based index used in python for
        lists. We internally translate this too and from the 1 based indexing
        used in the NITF file.'''
        if(self._type_support_tre):
            prepare_tre_write(self.tre_list, self.subheader,des_list,
                              self._tre_field_list, seg_index)

    def read_from_file(self, fh, seg_index=None):
        '''Read from a file. Note that we pass in the 0 based segment index 
        number. Most readers don't care at all about this, but it can be
        useful for implementing some external code readers (e.g., GDAL
        can read an image segment by the file name and index)'''
        self.subheader.read_from_file(fh)
        self._read_user_subheader()
        if self.nitf_file:
            hs = self.nitf_file.data_handle_set
        else:
            from .nitf_segment_data_handle import NitfSegmentDataHandleSet
            hs = NitfSegmentDataHandleSet.default_handle_set()
        self.data = hs.read_from_file(self, fh, seg_index)

    def _update_file_header(self, fh, seg_index, sz_header, sz_data):
        '''Update the NITF file header with the segment header and data size.'''
        self.nitf_file.file_header.update_field(fh,
              self._update_file_header_field[0], sz_header, (seg_index,))
        self.nitf_file.file_header.update_field(fh, 
              self._update_file_header_field[1], sz_data, (seg_index,))

    def _read_user_subheader(self):
        '''Read user subheader to the segment subheader'''
        if(self.nitf_file):
            hs = self.nitf_file.user_subheader_handle_set
        else:
            from .nitf_segment_user_subheader_handle import NitfSegmentUserSubheaderHandleSet
            hs = NitfSegmentUserSubheaderHandleSet.default_handle_set()
        cls = hs.user_subheader_cls(self)
        if not cls:
            return
        self.user_subheader = cls()
        fh = io.BytesIO(self.subheader.user_subheader_data)
        self.user_subheader.read_from_file(fh)

    def _write_user_subheader(self):
        '''Write user subheader to the segment subheader'''
        if(self.user_subheader):
            fh = io.BytesIO()
            self.user_subheader.write_to_file(fh)
            self.subheader.user_subheader_data = fh.getvalue()
        else:
            self.subheader.user_subheader_data = ""

    def write_to_file(self, fh, seg_index):
        '''Write to a file. We also update the file header information in 
        the nitf_file passed in with the header and data size for this segment.
        
        The nitf_file can be passed as None to skip the file header update. 
        This isn't generally used in real code, but it can be useful for unit
        tests (so testing a segment writing w/o needing a full NitfFile in the
        test).'''
        start_pos = fh.tell()
        if(self.nitf_file):
            cls = self.nitf_file.user_subheader_handle_set.user_subheader_cls(self)
            if cls and not isinstance(self.user_subheader, cls):
                raise RuntimeError("Require user_subheader of type %s" % cls)
        self._write_user_subheader()
        self.subheader.write_to_file(fh)
        sz_header = fh.tell() - start_pos
        start_pos = fh.tell()
        self.data.write_to_file(fh)
        sz_data = fh.tell() - start_pos
        # Normally nitf_file will be present, but for unit tests it
        # can be useful to skip this
        if(self.nitf_file):
            self._update_file_header(fh, seg_index, sz_header,
                                    sz_data)
        # Return value not normally needed, but can be useful for unit
        # tests.
        return (sz_header, sz_data)

class NitfImageSegment(NitfSegment):
    '''Image segment (IS), supports the standard image type of data.
    '''
    sh_class = NitfImageSubheader
    _update_file_header_field = ("lish", "li")
    _type_support_tre = True
    _tre_field_list = [["ixshdl", "ixofl", "ixshd"],
                       ["udidl", "udofl", "udid"]]

    def short_desc(self):
        return "ImageSegment %s" % self.subheader.iid1
    
    @property
    def image(self):
        '''Synonym for data, just a more descriptive name of content for
        a NitfImageSegment'''
        return self.data

    # Few properties from image subheader that we want at this level
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
    
    
class NitfGraphicSegment(NitfSegment):
    '''Graphic segment (GS), support the standard graphic type of data.'''
    sh_class = NitfGraphicSubheader
    _update_file_header_field = ("lssh", "ls")
    _type_support_tre = True
    _tre_field_list = [["sxshdl", "sxsofl", "sxshd"]]

    def short_desc(self):
        return "GraphicSegment %s \"%s\"" % (self.subheader.sid,
                                         self.subheader.sname)
    
    @property
    def graphic(self):
        '''Synonym for data, just a more descriptive name of content for
        a NitfGrapichSegment'''
        return self.data

class NitfTextSegment(NitfSegment):
    '''Text segment (TS), support the standard text type of data. 
    Note that txt can be either a str or bytes, whichever is most convenient
    for you. We encode/decode using utf-8 as needed. You can access the data
    as one or the other using data_as_bytes and data_as_str.'''
    sh_class = NitfTextSubheader
    _update_file_header_field = ("ltsh", "lt")
    _type_support_tre = True
    _tre_field_list = [["txshdl", "txsofl", "txshd"]]

    def short_desc(self):
        return "TextSegment %s" % self.subheader.textid
    
    @property
    def text(self):
        '''Synonym for data, just a more descriptive name of content for
        a NitfTextSegment'''
        return self.data

class NitfDesSegment(NitfSegment):
    '''Data extension segment (DES), allows for the addition of different data 
    types with each type encapsulated in its own DES'''
    sh_class = NitfDesSubheader
    _type_support_tre = False
    _update_file_header_field = ("ldsh", "ld")

    def short_desc(self):
        return "DesSegment %s" % self.subheader.desid

    @property
    def des(self):
        '''Synonym for data, just a more descriptive name of content for
        a NitfDesSegment'''
        return self.data
        
    def __str__(self):
        '''Text description of structure, e.g., something you can print out'''
        # Special case for TRE_OVERFLOW
        # Because we will print the data out as TREs later so we'll skip
        # printing here
        if(self.subheader.desid.encode("utf-8") == b'TRE_OVERFLOW'):
            return "TRE_OVERFLOW\n"
        return super().__str__()

class NitfResSegment(NitfSegment):
    '''Reserved extension segment (RES), non-standard data segment which is
    user-defined. A NITF file can support different user-defined types of 
    segments called RES.'''
    sh_class = NitfResSubheader
    _type_support_tre = False
    _update_file_header_field = ("lresh", "lre")
    
    def short_desc(self):
        return "ResSegment %s" % self.subheader.resid


# Add engrda to give hash access to ENGRDA TREs
add_engrda_function(NitfSegment)

# Add TRE finding functions
add_find_tre_function(NitfSegment)

__all__ = ["NitfSegment", "NitfImageSegment", "NitfGraphicSegment",
           "NitfTextSegment", "NitfDesSegment", "NitfResSegment",
           ]
