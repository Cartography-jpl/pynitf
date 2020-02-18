from .nitf_segment import NitfDesSegment, NitfResSegment
from .priority_handle_set import PriorityHandleSet
import abc
import copy

class NitfSegmentUserSubheaderHandleSet(object):
    '''This holds the user subheader handlers for each of the NitfSegment
    types that support these.'''
    def __init__(self):
        self.des_set = None
        self.res_set = None
    @classmethod
    def default_handle_set(cls):
        '''Return the default handle set to use.'''
        res = cls()
        res.des_set = copy.copy(DesUserSubheaderHandleSet.default_handle_set())
        res.res_set = copy.copy(ResUserSubheaderHandleSet.default_handle_set())
        return res
    def user_subheader_cls(self, seg):
        '''Return the user subheader class, or None if no User Subheader'''
        if(isinstance(seg, NitfDesSegment)):
            return self.des_set.handle(seg)
        elif(isinstance(seg, NitfResSegment)):
            return self.res_set.handle(seg)
        return None

class DesUserSubheaderHandleSet(PriorityHandleSet):
    def handle_h(self, h, seg):
        return h.user_subheader_cls(seg)

class ResUserSubheaderHandleSet(PriorityHandleSet):
    def handle_h(self, h, seg):
        return h.user_subheader_cls(seg)

class DesUserSubheaderHandle(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def user_subheader_cls(self, seg):
        pass

class ResUserSubheaderHandle(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def user_subheader_cls(self, seg):
        pass

class DesIdToUSHHandle(DesUserSubheaderHandle):
    def __init__(self):
        self.des_id_to_cls = {}
        
    def user_subheader_cls(self, seg):
        return(True, self.des_id_to_cls.get(seg.subheader.desid, None))

    def add_des_user_subheader(self, desid, cls):
        self.des_id_to_cls[desid] = cls

desid_to_user_subheader_handle = DesIdToUSHHandle()

DesUserSubheaderHandleSet.add_default_handle(desid_to_user_subheader_handle)

__all__ = ["desid_to_user_subheader_handle",
           "NitfSegmentUserSubheaderHandleSet",
           "DesUserSubheaderHandleSet",
           "ResUserSubheaderHandleSet",
           "DesUserSubheaderHandle",
           "ResUserSubheaderHandle",
           "DesIdToUSHHandle"]
