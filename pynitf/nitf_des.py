# We import a number of "private" classes from nitf_field. This module really
# is part of nitf_field.py, we have just pulled it out into a separate file
# to keep things clean
#
# Note when importing TREs that much of the documentation is in PDF tables.
# You can't easily paste this directly to emacs. But you can import to Excel.
# To do this, cut and paste the table into *Word*, and then cut and paste
# from word to Excel. For some reason, you can't go directly to Excel. You
# can then cut and paste from excel to emacs
from .nitf_field import FieldStruct
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
    def __init__(self, seg=None):
        NitfDes.__init__(self, seg)
        FieldStruct.__init__(self)
        self.data_start = None
        self.data_after_tre_size = None
        self.data_to_copy = None
        
    def read_from_file(self, fh, seg_index=None):
        if(self.subheader.desid != self.des_tag):
            return False
        t = fh.tell()
        FieldStruct.read_from_file(self,fh)
        self.data_start = fh.tell()
        self.data_after_tre_size = self._seg().data_size - (self.data_start - t)
        if(self.data_after_tre_size != 0):
            if(not self.data_after_allowed):
                raise RuntimeError("DES %s TRE length was expected to be %d but was actually %d" % (self.des_tag, self._seg().data_size, (self.data_start - t)))
            if(self.data_copy):
                self.data_to_copy = fh.read(self.data_after_tre_size)
            else:
                fh.seek(self.data_after_tre_size, 1)
        return True
        
    def write_to_file(self, fh):
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

class NitfDesFieldStructObjectHandle(NitfDesFieldStruct):
    '''This is a class where the DES is handled by an object type
    des_implementation_class in des_implementation_field. This
    possibly also include user defined subheaders.  See for example
    DesCSATTB in geocal.
    '''
    def read_from_file(self, fh, seg_index=None):
        if(DEBUG):
            print("Trying to match %s" % self.subheader.desid)
        if(self.subheader.desid != self.des_tag):
            if(DEBUG):
                print("Match failed")
            return False
        if(DEBUG):
            print("Match succeeded in constructor")
        setattr(self, self.des_implementation_field,
                self.des_implementation_class.des_read(fh))
        self.update_raw_field()
        return True
    
    def write_to_file(self, fh):
        getattr(self, self.des_implementation_field).des_write(fh)
        
    def str_hook(self, file):
        '''Convenient to have a place to add stuff in __str__ for derived
        classes. This gets called after the DES name is written, but before
        any fields. Default is to do nothing, but derived classes can 
        override this if desired.'''
        pass
    def __str__(self):
        '''Text description of structure, e.g., something you can print
        out.'''
        if(self._seg and self._seg().nitf_file and
           self._seg().nitf_file.report_raw):
            self.update_raw_field()
            return super().__str__()
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
        super().read_from_file(fh2)

# TODO May want to rework this, not sure if having handle_diff in the
# object is the right way to handle this.

class DesFieldStructObjectDiff(NitfDiffHandle):
    '''Compare two NitfDesObjectHandle.'''
    def handle_diff(self, des1, des2, nitf_diff):
        if(not isinstance(des1, NitfDesFieldStructObjectHandle) or
           not isinstance(des2, NitfDesFieldStructObjectHandle)):
            return (False, None)
        return (True, des1.handle_diff(des2))

NitfDiffHandleSet.add_default_handle(DesFieldStructObjectDiff())
    
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

def _create_attribute_forward_to_implementation_object(fname):
    def f(self):
        t = getattr(self, self.des_implementation_field)
        if(not hasattr(t, fname)):
            raise AttributeError("The implementation class %s does not have the field %s" %(self.des_implementation_class.__name__, fname))
        return getattr(t, fname)
    return property(f)
    

NitfSegmentDataHandleSet.add_default_handle(TreOverflow)
# Don't normally use, but you can add this if desired
#NitfSegmentDataHandleSet.add_default_handle(NitfDesCopy, priority_order=-999)

__all__ = [ "NitfDesCopy", "TreOverflow", "NitfDesFieldStruct",
            "NitfDesFieldStructObjectHandle"]

