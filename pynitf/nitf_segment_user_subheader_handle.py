from .nitf_segment import NitfDesSegment, NitfResSegment
from .priority_handle_set import PriorityHandleSet
import abc
import copy

class NitfSegmentUserSubheaderHandleSet(PriorityHandleSet):
    '''This holds the user subheader handlers for each of the NitfSegment
    types that support these.'''
    def handle_h(self, obj, seg):
        if obj.seg_class is not None and not isinstance(seg, obj.seg_class):
            return (False, None)
        return obj.user_subheader_cls(seg)
    
    def user_subheader_cls(self, seg):
        '''Return the user subheader class, or None if no User Subheader'''
        if(not isinstance(seg, NitfDesSegment) and
           not isinstance(seg, NitfResSegment)):
            return None
        return self.handle(seg)

class UserSubheaderHandle(object, metaclass=abc.ABCMeta):
    seg_class = None
    @abc.abstractmethod
    def user_subheader_cls(self, seg):
        pass

class DesIdToUSHHandle(UserSubheaderHandle):
    seg_class = NitfDesSegment
    def __init__(self):
        self.des_id_to_cls = {}
        
    def user_subheader_cls(self, seg):
        return(True, self.des_id_to_cls.get(seg.subheader.desid, None))

    def add_des_user_subheader(self, desid, cls):
        self.des_id_to_cls[desid] = cls

class ResIdToUSHHandle(UserSubheaderHandle):
    seg_class = NitfResSegment
    def __init__(self):
        self.res_id_to_cls = {}
        
    def user_subheader_cls(self, seg):
        return(True, self.res_id_to_cls.get(seg.subheader.resid, None))

    def add_res_user_subheader(self, resid, cls):
        self.res_id_to_cls[resid] = cls
        
desid_to_user_subheader_handle = DesIdToUSHHandle()
resid_to_user_subheader_handle = ResIdToUSHHandle()

NitfSegmentUserSubheaderHandleSet.add_default_handle(desid_to_user_subheader_handle)
NitfSegmentUserSubheaderHandleSet.add_default_handle(resid_to_user_subheader_handle)

__all__ = ["desid_to_user_subheader_handle",
           "resid_to_user_subheader_handle",
           "NitfSegmentUserSubheaderHandleSet",
           "UserSubheaderHandle",
           "DesIdToUSHHandle",
           "ResIdToUSHHandle",]
