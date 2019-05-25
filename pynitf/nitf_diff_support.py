from .nitf_file import *
from .nitf_field import _FieldLoopStruct
import logging
import six, abc, collections
import numpy as np

@six.add_metaclass(abc.ABCMeta)
class DiffHandle(object):
    '''Base class of handlers for looking at differences. We can have
    specialized classes that handle the differences.'''
    def __init__(self, logger=logging.getLogger('nitf_diff')):
        self.logger = logger

    exclude = None
    include = None

    @classmethod
    def set_exclude(cls, exclude):
        cls.exclude = exclude

    @classmethod
    def get_exclude(cls):
        return cls.exclude

    @classmethod
    def set_include(cls, include):
        cls.include = include

    @classmethod
    def get_include(cls):
        return cls.include

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

    def process_field_value_list(self, type, list1, parent1, list2, parent2):
        is_same = True

        for index, field in enumerate(list1):
            if (not isinstance(field, _FieldLoopStruct)):
                if (field.field_name is not None):
                    compare_name = field.field_name
                    if hasattr(field, 'name') and field.name != None:
                        compare_name = field.name
                        
                    exclude = DiffHandle.get_exclude()
                    if exclude != None:
                        if compare_name in exclude:
                            self.logger.debug('excluding ' + field.field_name)
                            continue

                    include = DiffHandle.get_include()
                    if include != None:
                        if not compare_name in include:
                            self.logger.debug('not including ' + field.field_name)
                            continue

                    if hasattr(field, 'eq_fun') and field.eq_fun != None:
                        this_is_same = field.eq_fun[0](field.value(parent1)[()], 
                                                       list2[index].value(parent2)[()], 
                                                       *field.eq_fun[1:])
                    else:
                        this_is_same = field.value(parent1) == list2[index].value(parent2)

                    if not this_is_same:
                        self.logger.error("%s 1 has field %s as %s while %s 2 has %s" %
                                          (type, field.field_name, str(field),
                                           type, str(list2[index])))
                        is_same = False
            else:
                is_same = self.process_field_value_list(type, field.field_value_list, parent1,
                                                        list2[index].field_value_list, parent2) \
                          and is_same

        self.logger.debug("process_field_value_list(%s) returning>>> %s" % (type, is_same))
        return is_same

    def compare_tres(self, tre1, tre2):
        return self.process_field_value_list('TRE', tre1.field_value_list, 
                                             tre1, tre2.field_value_list, tre2)

class DefaultHandle(DiffHandle):
    def __init__(self, logger=logging.getLogger('nitf_diff')):
        super().__init__(logger)
        
    def handle_diff(self, obj1, obj2):
        self.logger.debug("Using default always match handler")
        self.logger.debug("obj1: %s" % obj1.summary())
        self.logger.debug("obj2: %s" % obj2.summary())
        return (True, True)

class TREFileHeadHandle(DiffHandle):
    '''Handler for TRE and file headers.'''
    
    def __init__(self, TRE_file_head_type, logger=logging.getLogger('nitf_diff')):
        super().__init__(logger)
        assert TRE_file_head_type == 'TRE' or TRE_file_head_type == 'FileHead'
        self.obj_type = TRE_file_head_type

    def handle_diff(self, obj1, obj2):
        self.logger.debug("Using %s Handler" % self.obj_type)
        self.logger.debug("obj1: %s" % obj1.summary())
        self.logger.debug("obj2: %s" % obj2.summary())

        # Compare the fields of the two objects
        is_same = self.process_field_value_list(self.obj_type, 
                                                obj1.field_value_list, obj1, 
                                                obj2.field_value_list, obj2)

        self.logger.debug("TREFileHeadHandle(%s) returning>>> %s" % (self.obj_type, is_same))
        return (True, is_same)

class ISegHandle(DiffHandle):
    '''Handler for image segments.'''
    
    def __init__(self, logger=logging.getLogger('nitf_diff')):
        super().__init__(logger)

    def handle_diff(self, obj1, obj2):
        self.logger.debug("Using Image Segment Handler")
        self.logger.debug("obj1: %s" % obj1.summary())
        self.logger.debug("obj2: %s" % obj2.summary())

        # Compare the subheader of the two Image Segments
        is_same = self.process_field_value_list('Image',
                                                obj1.subheader.field_value_list, 
                                                obj1.subheader,
                                                obj2.subheader.field_value_list, 
                                                obj2.subheader)
        
        # Although the TREs are technically part of the image
        # subheader, _handle_type() checks all segments for tre_lists,
        # so we don't need to do it here.

        # Compare the pixels using default atol and rtol (see numpy allclose doc)
        is_same = is_same and np.allclose(obj1.data[:,:,:], obj2.data[:,:,:])

        self.logger.debug("ISegHandle returning>>> %s" % is_same)
        return (True, is_same)

class TSegHandle(DiffHandle):
    '''Handler for text segments.'''

    def __init__(self, logger=logging.getLogger('nitf_diff')):
        super().__init__(logger)

    def handle_diff(self, obj1, obj2):
        self.logger.debug("Using Text Handler")
        self.logger.debug("obj1: %s" % obj1.summary())
        self.logger.debug("obj2: %s" % obj2.summary())

        # Compare the subheaders of the two Text Segments
        is_same = self.process_field_value_list('Text',
                                                obj1.subheader.field_value_list, 
                                                obj1.subheader,
                                                obj2.subheader.field_value_list, 
                                                obj2.subheader)
        
        # Although the TREs are technically part of the subheaders,
        # _handle_type() checks all segments for tre_lists, so we
        # don't need to do it here.

        # Compare the object data
        is_same = is_same and obj1.data_as_str == obj2.data_as_str

        self.logger.debug("TSegHandle returning>>> %s" % is_same)
        return (True, is_same)

class DSegHandle(DiffHandle):
    '''Handler for data extension segments.'''

    def __init__(self, logger=logging.getLogger('nitf_diff')):
        super().__init__(logger)

    def handle_diff(self, obj1, obj2):
        self.logger.debug("Using DES Handler")
        self.logger.debug("obj1: %s" % obj1.summary())
        self.logger.debug("obj2: %s" % obj2.summary())

        # Compare the subheaders of the two DES Segments
        is_same = self.process_field_value_list("DES_SH",
                                                obj1.subheader.field_value_list, 
                                                obj1.subheader,
                                                obj2.subheader.field_value_list, 
                                                obj2.subheader)
        
        # Although the TREs are technically part of the subheaders,
        # _handle_type() checks all segments for tre_lists, so we
        # don't need to do it here.


        #Compare User-Defined Subheaders
        # Compare the subheaders of the two DES Segments
        #self.logger.debug(str(dir(obj1.des)))
        #self.logger.debug(str(dir(obj1.des.user_subheader)))
        is_same = self.process_field_value_list("DES_UH",
                                                obj1.des.user_subheader.field_value_list,
                                                obj1.des.user_subheader,
                                                obj2.des.user_subheader.field_value_list,
                                                obj2.des.user_subheader) and is_same

        # TODO: compare DES payloads
        #self.logger.debug(str(dir(obj1.data)))
        is_same = self.process_field_value_list("DES_DATA",
                                                obj1.des.field_value_list,
                                                obj1.des,
                                                obj2.des.field_value_list,
                                                obj2.des) and is_same

        self.logger.debug("DSegHandle returning>>> %s" % is_same)
        return (True, is_same)

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

register_file_header_handle(TREFileHeadHandle("FileHead"), priority_order=1000)    
register_iseg_handle(ISegHandle(), priority_order=1000)
register_tre_handle(TREFileHeadHandle("TRE"), priority_order=1000)    
register_tseg_handle(TSegHandle(), priority_order=1000)    
register_dseg_handle(DSegHandle(), priority_order=1000)    

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
            logger.debug("Comparing %d tres of %s index %d" % 
                         (min(len(lis1[i].tre_list), len(lis2[i].tre_list)), nm, i))
            for j in range(min(len(lis1[i].tre_list),
                               len(lis2[i].tre_list))):
                status = tre_handle.handle_diff(lis1[i].tre_list[j],
                                           lis2[i].tre_list[j])
                is_same = is_same and status
    return is_same
    
def nitf_file_diff(f1_name, f2_name, exclude = None, include = None):
    '''Compare 2 NITF files. This returns an overall status of True
    if the files compare the same, false otherwise. The exclude and
    include lists of names like 'image.iid1' are used to control
    which items are compared. The names are defined in, e.g.
    image.iid1 in nitf_image_subheader.desc. See also
    nitf_field.create_nitf_field_structure.

    We print out messages to the logger 'nitf_diff'.
    '''

    DiffHandle.set_exclude(exclude)
    DiffHandle.set_include(include)

    logger=logging.getLogger('nitf_diff')
    f1 = NitfFile(f1_name)
    f2 = NitfFile(f2_name)
    is_same = True
    status = file_header_handle.handle_diff(f1.file_header, f2.file_header)
    is_same = is_same and status

    # We should probably have a more intelligent matching of TRE, image
    # segment, etc. Files shouldn't different just because the order is
    # different. But for now, this fails.

    logger.debug("Comparing %d file-level TREs" % min(len(f1.tre_list),
                                                 len(f2.tre_list)))
    if(len(f1.tre_list) != len(f2.tre_list)):
        logger.error("File 1 has %d file level TREs while file 2 has %d" %
                     (len(f1.tre_list), len(f2.tre_list)))
        is_same = False
    for i in range(min(len(f1.tre_list), len(f2.tre_list))):
        status = tre_handle.handle_diff(f1.tre_list[i], f2.tre_list[i])
        is_same = is_same and status

    logger.debug("Comparing image segments")
    status = _handle_type(f1.image_segment, f2.image_segment, 
                          "image segment", iseg_handle, logger)
    is_same = is_same and status

    logger.debug("Comparing text segments")
    staus = _handle_type(f1.text_segment, f2.text_segment, 
                         "text segment", tseg_handle, logger)
    is_same = is_same and status

    logger.debug("Comparing des segments")
    status = _handle_type(f1.des_segment, f2.des_segment, 
                          "des segment", dseg_handle, logger)
    is_same = is_same and status

    return is_same

__all_= ["DiffHandle", "DefaultHandle", "register_file_header_handle",
         "register_iseg_handle", "register_tre_handle",
         "register_tseg_handle", "register_dseg_handle",
         "nitf_file_diff"]
