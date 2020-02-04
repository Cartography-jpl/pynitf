from .nitf_file import *
from .nitf_field import _FieldLoopStruct
import logging
import abc, collections
import numpy as np
from .nitf_image import NitfImagePlaceHolder
from .nitf_tre import TreUnknown

#********************************************************
# NOTE! This code is all being replaced with a reorganization
# of NitfDiff. Left in place here until we get all the
# functionality moved over
#********************************************************

class DiffHandle(object, metaclass=abc.ABCMeta):
    '''Base class of handlers for looking at differences. We can have
    specialized classes that handle the differences.'''
    def __init__(self, logger=logging.getLogger('nitf_diff')):
        self.logger = logger

    exclude = None
    include = None
    config = None

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

    @classmethod
    def set_config(cls, config):
        cls.config = config

    @classmethod
    def get_config(cls):
        return cls.config

    def handle_diff(self, obj1, obj2, index=-1):
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
                    #print(compare_name)

                    val1 = None
                    val2 = None

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
                        val1 = field.value(parent1)[()]
                        val2 = list2[index].value(parent2)[()]
                        this_is_same = field.eq_fun[0](val1,
                                                       val2,
                                                       *field.eq_fun[1:])
                    else:
                        val1 = field.value(parent1)
                        val2 = list2[index].value(parent2)
                        this_is_same = val1 == val2

                    if not this_is_same:

                        # Convert values into strings and truncate so that it's easier to print out the result
                        val1 = str(val1)
                        val2 = str(val2)
                        if len(val1) > 100:
                            val1 = val1[:200] + "..."
                        if len(val2) > 100:
                            val2 = val2[:200] + "..."

                        self.logger.error("%s 1 has field %s as %s while %s 2 has %s" %
                                          (type, field.field_name, val1,
                                           type, val2))
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
        
    def handle_diff(self, obj1, obj2, index=-1):
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

    def handle_diff(self, obj1, obj2, index=-1):
        self.logger.debug("Using %s Handler" % self.obj_type)
        self.logger.debug("obj1: %s" % obj1.summary())
        self.logger.debug("obj2: %s" % obj2.summary())

        is_same = False
        try:
            if isinstance(obj1, TreUnknown) and isinstance(obj2, TreUnknown):
                is_same = (obj1 == obj2)
            else:
                # Compare the fields of the two objects
                is_same = self.process_field_value_list(self.obj_type,
                                                obj1.field_value_list, obj1, 
                                                obj2.field_value_list, obj2)
        except Exception as e:
            compared = "FileHead"
            if (self.obj_type == 'TRE'):
                compared = obj1.tre_tag
            self.logger.warning("Error while comparing " + compared +": "+ str(e))

        self.logger.debug("TREFileHeadHandle(%s) returning>>> %s" % (self.obj_type, is_same))
        return (True, is_same)

class ISegHandle(DiffHandle):
    '''Handler for image segments.'''
    
    def __init__(self, logger=logging.getLogger('nitf_diff')):
        super().__init__(logger)

    def handle_diff(self, obj1, obj2, index=-1):
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

        if isinstance(obj1.data, NitfImagePlaceHolder) or isinstance(obj2.data, NitfImagePlaceHolder):
            is_same = is_same and obj1.data == obj2.data
        else:
            if obj1.data.shape == obj2.data.shape:
                tolerance_config = None
                if index != -1 and self.config is not None \
                        and 'tolerances' in self.config and 'method' in self.config['tolerances'][index]:
                    tolerance_config = self.config['tolerances'][index]

                    if tolerance_config['method'] == "histogram" and 'numBins' in tolerance_config:
                        min1 = 0
                        min2 = 0
                        max1 = 0
                        max2 = 0
                        if np.issubdtype(obj1.data.dtype, np.integer):
                            min1 = np.iinfo(obj1.data.dtype).min
                            min2 = np.iinfo(obj2.data.dtype).min
                            max1 = np.iinfo(obj1.data.dtype).max
                            max2 = np.iinfo(obj2.data.dtype).max
                        else:
                            min1 = np.finfo(obj1.data.dtype).min
                            min2 = np.finfo(obj2.data.dtype).min
                            max1 = np.finfo(obj1.data.dtype).max
                            max2 = np.finfo(obj2.data.dtype).max

                        hist1, bins1 = np.histogram(obj1.data[:,:,:].ravel(), tolerance_config['numBins'], [min1, max1])
                        hist2, bins2 = np.histogram(obj2.data[:,:,:].ravel(), tolerance_config['numBins'], [min2, max2])
                        if 'percent' in tolerance_config:
                            is_same = is_same and np.allclose(hist1, hist2, rtol=tolerance_config['percent']/100)
                        elif 'value' in tolerance_config:
                            is_same = is_same and np.allclose(hist1, hist2, rtol=tolerance_config['value'])
                    elif tolerance_config['method'] == "count":
                        temp = obj1.data[:, :, :] - obj2.data[:, :, :]
                        count = np.count_nonzero(obj1.data[:, :, :] - obj2.data[:, :, :])
                        total = obj1.data[:, :, :].size
                        if 'percent' in tolerance_config:
                            is_same = is_same and (count < (total * (tolerance_config['percent']/100)))
                        elif 'value' in tolerance_config:
                            is_same = is_same and (count < (total * tolerance_config['value']))
                    elif tolerance_config['method'] == "value":
                        if 'percent' in tolerance_config:
                            is_same = is_same and np.allclose(obj1.data[:, :, :], obj2.data[:, :, :],
                                                              rtol=tolerance_config['percent']/100)
                        elif 'value' in tolerance_config:
                            is_same = is_same and np.allclose(obj1.data[:,:,:], obj2.data[:,:,:],
                                                              rtol=tolerance_config['value'])
                else:
                    is_same = is_same and np.allclose(obj1.data[:, :, :], obj2.data[:, :, :])
            else:
                is_same = is_same and False

        self.logger.debug("ISegHandle returning>>> %s" % is_same)
        return (True, is_same)

class TSegHandle(DiffHandle):
    '''Handler for text segments.'''

    def __init__(self, logger=logging.getLogger('nitf_diff')):
        super().__init__(logger)

    def handle_diff(self, obj1, obj2, index=-1):
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
    '''Handler for data extension segments.

    Note for a special DES (e.g. one handled by a C++ class) it can be
    useful to define "handle_diff". If this is present, we pass off the 
    difference to this function (which should return True if objects are 
    the same, False otherwise)'''

    def __init__(self, logger=logging.getLogger('nitf_diff')):
        super().__init__(logger)

    def handle_diff(self, obj1, obj2, index=-1):
        self.logger.debug("Using DES Handler")
        self.logger.debug("obj1: %s" % obj1.summary())
        self.logger.debug("obj2: %s" % obj2.summary())
        if hasattr(obj1, 'handle_diff'):
            return (True, obj1.handle_diff(obj2))

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

        # Compare DES payloads
        if hasattr(obj1.des, 'handle_diff'):
            is_same = obj1.des.handle_diff(obj2.des) and is_same
        elif hasattr(obj1.des, 'data'):
            is_same = np.array_equal(obj1.des.data, obj2.des.data)
        else:
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

    def set_config(self, config):
        for k in sorted(self.handle_list.keys()):
            for handle in self.handle_list[k]:
                handle.set_config(config)

    def handle_diff(self, obj1, obj2, index=-1):
        '''Go through list of handles for the objects. This returns
        True if the objects compare as the same, False otherwise.'''
        for k in sorted(self.handle_list.keys()):
            for handle in self.handle_list[k]:
                hflag, res = handle.handle_diff(obj1, obj2, index)
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
        status = handler.handle_diff(lis1[i], lis2[i], i)
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
    
def nitf_file_diff(f1_name, f2_name, exclude = None, include = None, config = None):
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
    DiffHandle.set_config(config)

    # file_header_handle.set_config(config)
    # iseg_handle.set_config(config)
    # tre_handle.set_config(config)
    # tseg_handle.set_config(config)
    # dseg_handle.set_config(config)

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
    status = _handle_type(f1.text_segment, f2.text_segment,
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
