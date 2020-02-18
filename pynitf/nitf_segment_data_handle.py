from .nitf_segment import (NitfImageSegment, NitfDesSegment, NitfTextSegment,
                           NitfGraphicSegment, NitfResSegment)
from .priority_handle_set import PriorityHandleSet
import abc
import copy

class NitfSegmentDataHandleSet(PriorityHandleSet):
    '''Handle reading the data in a segment (e.g, a image)'''
    def read(seg, fh, seg_index=None):
        '''Read the data for the given NitfSegment from file handle fh.

        Note that most handlers don't care about the seg_index, but there
        are some that hand things off other libraries that do use this
        information (e.g. NitfImageGdal found in GeoCal). So we hand off
        this information if we have the seg_index available (e.g., we
        are calling this through NitfFile).'''
        self.handle(seg, fh, seg_index)
        
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
    def __init__(seg = None):
        '''Initialize object. If the NitfSegment we are associated with
        gets passed in then we use the subheader and if available 
        user_subheader found in that segment. Otherwise we create new
        instances of the classes given by sh_class and uh_class.'''
        self.seg = seg
        if seg:
            self.subheader = seg.subheader
            self.user_subheader = seg.user_subheader
            
#    read_from_file should
#      return True if this class can
#      handle the type, and False
#      otherwise.
    
    
    
