from .nitf_field import FieldStruct, FieldStructDiff
from .nitf_segment_data_handle import (NitfDes,
                                       NitfSegmentDataHandleSet)
from .nitf_diff_handle import (NitfDiffHandle, NitfDiffHandleSet,
                               DiffContextFilter)
import copy
import io
import logging

DEBUG = False

logger = logging.getLogger('nitf_diff')

class NitfDesFieldStruct(NitfDes, FieldStruct):
    '''There is a class of DES that are essentially like big TREs. The data
    is just a bunch of field data, possibly with user defined subheaders.
    See for example DesCSATTB.

    This base class handles this case.
    
    The TRE may or may not be followed by data. If it isn't, then we report
    an error if all the data isn't read.
    '''
    data_after_allowed = None
    data_copy = None
    # If defined, we have the DES handled by an object type
    # des_implementation_class in des_implementation_field.
    # See for example DesCSATTB in geocal.
    des_implementation_field = None
    des_implementation_class = None
    
    def __init__(self, seg=None):
        NitfDes.__init__(self, seg)
        FieldStruct.__init__(self)
        self.data_start = None
        self.data_after_tre_size = None
        self.data_to_copy = None
        
    def read_from_file(self, fh, seg_index=None, force_raw_read=False):
        if(self.subheader.desid != self.des_tag):
            return False
        if(self.des_implementation_field and not force_raw_read):
            setattr(self, self.des_implementation_field,
                    self.des_implementation_class.des_read(fh))
            self.update_raw_field()
            return True
        t = fh.tell()
        FieldStruct.read_from_file(self,fh)
        self.data_start = fh.tell()
        if(self._seg is not None):
            self.data_after_tre_size = self._seg().data_size - (self.data_start - t)
        else:
            self.data_after_tre_size = 0
        if(self.data_after_tre_size != 0):
            if(not self.data_after_allowed):
                raise RuntimeError("DES %s TRE length was expected to be %d but was actually %d" % (self.des_tag, self._seg().data_size, (self.data_start - t)))
            if(self.data_copy):
                self.data_to_copy = fh.read(self.data_after_tre_size)
            else:
                fh.seek(self.data_after_tre_size, 1)
        return True
        
    def write_to_file(self, fh):
        if(self.des_implementation_field):
            getattr(self, self.des_implementation_field).des_write(fh)
        else:
            FieldStruct.write_to_file(self, fh)
            if(self.data_to_copy):
                fh.write(self.data_to_copy)
            
    def str_hook(self, file):
        '''Convenient to have a place to add stuff in __str__ for derived
        classes. This gets called after the DES name is written, but before
        any fields. Default is to do nothing, but derived classes can 
        override this if desired.'''
        pass
    
    def __str__(self):
        '''Text description of structure, e.g., something you can print
        out.'''
        if(not self.des_implementation_field or
           (self._seg and self._seg().nitf_file and
            self._seg().nitf_file.report_raw)):
            self.update_raw_field()
            res = io.StringIO()
            self.str_hook(res)
            if(self.user_subheader):
                print("User-Defined Subheader: ", file=res)
                print(self.user_subheader, file=res)
            print(FieldStruct.__str__(self), file=res)
            if(self.data_after_tre_size and self.data_after_tre_size != 0):
                print("Extra data of length %d" % self.data_after_tre_size,
                      file=res)
            return res.getvalue()
        res = io.StringIO()
        self.str_hook(res)
        if(self.user_subheader):
            print("User-Defined Subheader: ", file=res)
            print(self.user_subheader, file=res)
        print("Object associated with DES:", file=res)
        print(getattr(self, self.des_implementation_field), file=res)
        return res.getvalue()

    def update_raw_field(self):
        '''Update the raw fields after a change to des_implementation_field'''
        fh = io.BytesIO()
        self.write_to_file(fh)
        fh2 = io.BytesIO(fh.getvalue())
        self.read_from_file(fh2, force_raw_read=True)
    
class DesFieldStructDiff(FieldStructDiff):
    '''Compare two NitfDesObjectHandle.'''
    def configuration(self, nitf_diff):
        return self._config
    def handle_diff(self, des1, des2, nitf_diff):
        if(not isinstance(des1, NitfDesFieldStruct) or
           not isinstance(des2, NitfDesFieldStruct)):
            return (False, None)
        if(des1.des_tag != des2.des_tag):
            logger.difference("DES tags don't match. DES 1 '%s' and DES 2 '%s'",
                              des.des_tag, des.des_tag)
            return (True, False)
        # If we have a handle_diff function use it. 
        if(hasattr(des1, "handle_diff")):
            return (True, des1.handle_diff(des2))
        # Otherwise compare the fields
        self._config = nitf_diff.config.get("DES", {}).get(des1.des_tag, {})
        with nitf_diff.diff_context("DES '%s'" % des1.des_tag, add_text = True):
            return (True, self.compare_obj(des1, des2, nitf_diff))

NitfDiffHandleSet.add_default_handle(DesFieldStructDiff())
NitfDiffHandleSet.default_config["DES"] = {}
    
class NitfDesCopy(NitfDes):
    '''Implementation that reads from one file and just copies to the other.
    Not normally registered, but can be useful to use for some test cases (e.g.
    want to copy over an unimplemented DES)'''
    def __init__(self, seg=None):
        super().__init__(seg)
        self.data = None

    def __str__(self):
        return "NitfDesCopy %d bytes of data" % (len(self.data))
        
    def read_from_file(self, fh, seg_index=None):
        self.data = fh.read(self._seg().data_size)
        return True

    def write_to_file(self, fh):
        '''Write an DES to a file.'''
        if(self.data is None): 
            raise RuntimeError("Can only write data after we have read it in NitdDesCopy")
        fh.write(self.data)
    
class TreOverflow(NitfDes):
    '''DES used to handle TRE overflow.'''
    des_tag = "TRE_OVERFLOW"
    def __init__(self, seg=None, seg_index=None, overflow=None):
        '''Note that seg_index should be the normal 0 based index python
        uses elsewhere. Internal to the DES we translate this to the 1 based
        index that NITF uses.'''
        super().__init__(seg)
        if(seg is None):
            self.subheader.desoflw = str.upper(overflow)
            self.subheader.desitem = seg_index+1
        self.data = None

    def read_from_file(self, fh, seg_index=None):
        '''Read an DES from a file.'''
        if(self.subheader.desid != self.des_tag):
            return False
        self.data = fh.read(self._seg().data_size)
        return True
    
    def write_to_file(self, fh):
        '''Write to a file.'''
        fh.write(self.data)
        
    def __str__(self):
        '''Text description of structure, e.g., something you can print
        out.'''
        return "TreOverflow"

NitfSegmentDataHandleSet.add_default_handle(TreOverflow)
# Don't normally use, but you can add this if desired
#NitfSegmentDataHandleSet.add_default_handle(NitfDesCopy, priority_order=-999)

__all__ = [ "NitfDesCopy", "TreOverflow", "NitfDesFieldStruct",]

