from .nitf_file import *
import logging
import six, abc, collections

@six.add_metaclass(abc.ABCMeta)
class DiffHandle(object):
    '''Base class of handlers for looking at differences. We can have
    specialized classes that handle the differences.'''
    def __init__(self, logger=logging.getLogger('nitf_diff')):
        self.logger = logger

    def handle_diff(self, obj1, obj2):
        '''Handle the difference between 2 objects. Note that many of
        the handles can't handle a particular object. We use a chain of
        responsibility pattern here.
        
        Derived classes should return a tuple. The first value is true
        if we handled the objects, false otherwise. The second value
        is true if the objects compared as the same, false otherwise.

        Output about differences should be written using the logger 
        object.'''
        raise NotImplementedError()

class DefaultHandle(DiffHandle):
    def __init__(self, logger=logging.getLogger('nitf_diff')):
        super().__init__(logger)
        
    def handle_diff(self, obj1, obj2):
        self.logger.debug("Using default always match handler")
        self.logger.debug("obj1: %s" % obj1.summary())
        self.logger.debug("obj2: %s" % obj2.summary())
        return (True, True)

class DiffHandleList(object):
    '''Small class to handle to list of DiffHandle objects. This is little more
    complicated than just a list of handlers. The extra piece is allowing
    a priority_order to be assigned to the handlers, we look for 
    lower number first. 

    This is a chain-of-responsibility pattern, with the addition of an
    ordering based on a priority_order.
    '''
    def __init__(self):
        self.handle_list = collections.defaultdict(lambda : set())

    def add_handle(self, handle, priority_order=0):
        self.handle_list[priority_order].add(handle)

    def handle_diff(self, obj1, obj2):
        '''Go through list of handles for the objects. This returns
        True if the objects compare as the same, False otherwise.'''
        for k in sorted(self.handle_list.keys()):
            for handle in self.handle_list[k]:
                hflag, res = handle.handle_diff(obj1, obj2)
                if(hflag):
                    return res;
        raise RuntimeError("No handle found. Obj1 %s, Obj2 %s" % (obj1, obj2))

file_header_handle = DiffHandleList()
iseg_handle = DiffHandleList()
tre_handle = DiffHandleList()
tseg_handle = DiffHandleList()
dseg_handle = DiffHandleList()

def register_file_header_handle(handle, priority_order=0):
    file_header_handle.add_handle(handle, priority_order)

def register_iseg_handle(handle, priority_order=0):
    iseg_handle.add_handle(handle, priority_order)

def register_tre_handle(handle, priority_order=0):
    tre_handle.add_handle(handle, priority_order)

def register_tseg_handle(handle, priority_order=0):
    tseg_handle.add_handle(handle, priority_order)

def register_dseg_handle(handle, priority_order=0):
    dseg_handle.add_handle(handle, priority_order)

register_file_header_handle(DefaultHandle(), priority_order=1000)    
register_iseg_handle(DefaultHandle(), priority_order=1000)    
register_tre_handle(DefaultHandle(), priority_order=1000)    
register_tseg_handle(DefaultHandle(), priority_order=1000)    
register_dseg_handle(DefaultHandle(), priority_order=1000)    

def _handle_type(lis1, lis2, nm, handler, logger):
    is_same = True
    if(len(lis1) != len(lis2)):
        logger.error("File 1 has %d file level %s while file 2 has %d" %
                     (len(lis1), nm, len(lis2)))
        is_same = False
    logger.debug("Comparing %d %s" % (min(len(lis1), len(lis2)), nm))
    for i in range(min(len(lis1), len(lis2))):
        status = handler.handle_diff(lis1[i], lis2[i])
        is_same = is_same and status
        if(hasattr(lis1[i], "tre_list")):
            if(len(lis1[i].tre_list) != len(lis2[i].tre_list)):
                logger.error("File 1 has %d %s level TREs while file 2 has %d" %
                             (len(lis1[i].tre_list),
                              nm,
                              len(lis2[i].tre_list)))
                is_same = False
            logger.debug("Comparing %d tres of %s index %d" % (min(len(lis1[i].tre_list), len(lis2[i].tre_list)), nm, i))
            for j in range(min(len(lis1[i].tre_list),
                               len(lis2[i].tre_list))):
                status = tre_handle.handle_diff(lis1.tre_list[j],
                                           lis2.tre_list[j])
                is_same = is_same and status
    return is_same
    
def nitf_file_diff(f1_name, f2_name):
    '''Compare 2 NITF files. This returns an overall status of True
    if the files compare the same, false otherwise.

    We print out messages to the logger 'nitf_diff'.
    '''
    logger=logging.getLogger('nitf_diff')
    f1 = NitfFile(f1_name)
    f2 = NitfFile(f2_name)
    is_same = True
    status = file_header_handle.handle_diff(f1.file_header, f2.file_header)
    is_same = is_same and status
    # We should probably have a more intelligent matching of TRE, image
    # segment, etc. Files shouldn't different just because the order is
    # different. But for now, this fails
    logger.debug("Comparing %d file level" % min(len(f1.tre_list),
                                                 len(f2.tre_list)))
    if(len(f1.tre_list) != len(f2.tre_list)):
        logger.error("File 1 has %d file level TREs while file 2 has %d" %
                     (len(f1.tre_list), len(f2.tre_list)))
        is_same = False
    for i in range(min(len(f1.tre_list), len(f2.tre_list))):
        status = tre_handle.handle_diff(f1.tre_list[i], f2.tre_list[i])
        is_same = is_same and status
    status = _handle_type(f1.image_segment, f2.image_segment, "image segment",
                          iseg_handle, logger)
    is_same = is_same and status
    staus = _handle_type(f1.text_segment, f2.text_segment, "text segment",
                         tseg_handle, logger)
    is_same = is_same and status
    status = _handle_type(f1.des_segment, f2.des_segment, "des segment",
                          dseg_handle, logger)
    is_same = is_same and status
    return is_same

__all_= ["DiffHandle", "DefaultHandle", "register_file_header_handle",
         "register_iseg_handle", "register_tre_handle",
         "register_tseg_handle", "register_dseg_handle",
         "nitf_file_diff"]
