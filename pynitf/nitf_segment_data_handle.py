from .nitf_segment import (NitfImageSegment, NitfDesSegment, NitfTextSegment,
                           NitfGraphicSegment, NitfResSegment)
from .nitf_image_subheader import NitfImageSubheader
from .nitf_des_subheader import NitfDesSubheader
from .nitf_text_subheader import NitfTextSubheader
from .nitf_graphic_subheader import NitfGraphicSubheader
from .nitf_res_subheader import NitfResSubheader
from .priority_handle_set import PriorityHandleSet
import abc

class NitfSegmentDataHandleSet(PriorityHandleSet):
    '''Handle reading the data in a segment (e.g, a image)'''
    def read_from_file(self, seg, fh, seg_index=None):
        '''Read the data for the given NitfSegment from file handle fh.

        Note that most handlers don't care about the seg_index, but there
        are some that hand things off other libraries that do use this
        information (e.g. NitfImageGdal found in GeoCal). So we hand off
        this information if we have the seg_index available (e.g., we
        are calling this through NitfFile).'''
        return self.handle(seg, fh, seg_index)
        
    def handle_h(self, cls, seg, fh, seg_index):
        '''Try reading using a given cls derived from NitfData. We 
        first check that the seg is the same class as cls.seg_class,
        and if so try to read the data from file.
        '''
        if not isinstance(seg, cls.seg_class):
            return (False, None)
        t = cls(seg = seg)
        could_handle = t.read_from_file(fh, seg_index)
        if not could_handle:
            return (False, None)
        return (True, t)

class NitfData(object, metaclass=abc.ABCMeta):
    ''' Handle reading and writing the data in a segment (e.g, a image).'''
    seg_class = None
    sh_class = None
    uh_class = None
    def __init__(self, seg = None):
        '''Initialize object. If the NitfSegment we are associated with
        gets passed in then we use the subheader and if available 
        user_subheader found in that segment. Otherwise we create new
        instances of the classes given by sh_class and uh_class.'''
        self.seg = seg
        if seg:
            self.subheader = seg.subheader
            self.user_subheader = seg.user_subheader
        else:
            self.subheader = self.sh_class()
            if(self.uh_class):
                self.user_subheader = self.uh_class()
            else:
                self.user_subheader = None
                
    @abc.abstractmethod
    def read_from_file(self, fh, seg_index = None):
        '''Attempt to read data from the given file.  If the data can't be
        read this class, return False. Otherwise, return True. Note that
        True/False *isn't* from a read error, but rather because this
        is an unsupported type (e.g., a JPEG-2000 compressed image with
        a reader that doesn't support that).'''
        raise NotImplementedError

    @abc.abstractmethod
    def write_to_file(self, fh):
        '''Write data to the given file handle.'''
        raise NotImplementedError
                
    @property
    def security(self):
        '''NitfSecurity for data.'''
        return self.subheader.security

    @security.setter
    def security(self, v):
        '''Set NitfSecurity for data.'''
        self.subheader.security = v
    
class NitfImage(NitfData):
    '''Base class for reading/writing data in a NitfImageSegment'''
    seg_class = NitfImageSegment
    sh_class = NitfImageSubheader
    @property
    def shape(self):
        '''Return shape of data'''
        return self.subheader.shape

    @property
    def dtype(self):
        '''Return data type of data'''
        return self.subheader.dtype

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
    

class NitfDes(NitfData):
    '''Base class for reading/writing data in a NitfDesSegment'''
    seg_class = NitfDesSegment
    sh_class = NitfDesSubheader

class NitfText(NitfData):
    '''Base class for reading/writing data in a NitfTextSegment'''
    seg_class = NitfTextSegment
    sh_class = NitfTextSubheader
    
class NitfGraphic(NitfData):
    '''Base class for reading/writing data in a NitfGraphicSegment'''
    seg_class = NitfGraphicSegment
    sh_class = NitfGraphicSubheader

class NitfRes(NitfData):
    '''Base class for reading/writing data in a NitfResSegment'''
    seg_class = NitfResSegment
    sh_class = NitfResSubheader
    
    
    
