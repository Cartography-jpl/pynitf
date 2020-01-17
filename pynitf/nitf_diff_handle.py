from .priority_handle_set import PriorityHandleSet
import logging

logger = logging.getLogger('nitf_diff')

class NitfDiffHandleSet(PriorityHandleSet):
    default_config = {}
    def handle_h(self, h, obj1, obj2, nitf_diff):
        return h.handle_diff(obj1, obj2, nitf_diff)

class NitfDiffHandle(object):
    '''Base class for handling difference between two NITF object. Like always,
    you don't need to actually derive from this class if for whatever reason
    this isn't convenient but you should provide this interface.'''
    def handle_diff(self, obj1, obj2, nitf_diff):
        '''Handle determining difference between object. Returns a tuple, with
        the first value indicating if we can handle the types and the second
        indicating if the objects are the same.

        So, if we can't handle this particular set of objects, this
        returns (False, None).  Otherwise, it returns (True, True) if
        the objects are the "same" and (True, False) if they are
        different.'''
        raise NotImplementedError()

class AlwaysTrueHandle(NitfDiffHandle):
    '''Handle that always says things are equal. Nice for various test cases
    where we want to check for only a subset of things.'''
    def handle_diff(self, obj1, obj2, nitf_diff):
        logger.info("Using default always match handler")
        logger.info("obj1: %s" % obj1.summary())
        logger.info("obj2: %s" % obj2.summary())
        return (True, True)

__all__ = ["AlwaysTrueHandle", "NitfDiffHandle", "NitfDiffHandleSet",]
