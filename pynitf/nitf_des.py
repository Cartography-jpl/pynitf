# We import a number of "private" classes from nitf_field. This module really
# is part of nitf_field.py, we have just pulled it out into a separate file
# to keep things clean
#
# Note when importing TREs that much of the documentation is in PDF tables.
# You can't easily paste this directly to emacs. But you can import to Excel.
# To do this, cut and paste the table into *Word*, and then cut and paste
# from word to Excel. For some reason, you can't go directly to Excel. You
# can then cut and paste from excel to emacs
from .nitf_field import (FieldData, _FieldStruct, _FieldLoopStruct, 
                         _create_nitf_field_structure,
                         create_nitf_field_structure)
from .nitf_segment_data_handle import (NitfDes,
                                       NitfSegmentDataHandleSet)
from .nitf_diff_handle import (NitfDiffHandle, NitfDiffHandleSet,
                               DiffContextFilter)
import copy
import io
import logging

DEBUG = False

logger = logging.getLogger('nitf_diff')

class NitfDesFieldStruct(NitfDes, _FieldStruct):
    '''There is a class of DES that are essentially like big TREs. The data
    is just a bunch of field data, possibly with user defined subheaders.
    See for example DesCSATTB.

    This base class handles this case.
    
    Note that although you can directly create a class based on this one,
    there is also the create_nitf_des_structure function that automates 
    creating this from a table like we do with TREs.

    The TRE may or may not be followed by data. If it isn't, then we report
    an error if all the data isn't read.
    '''
    data_after_allowed = None
    data_copy = None
    def __init__(self, seg=None):
        NitfDes.__init__(self, seg)
        _FieldStruct.__init__(self)
        self.data_start = None
        self.data_after_tre_size = None
        self.data_to_copy = None
        
    def read_from_file(self, fh, seg_index=None, nitf_literal = False):
        if(self.subheader.desid != self.des_tag):
            return False
        t = fh.tell()
        _FieldStruct.read_from_file(self,fh, nitf_literal)
        self.data_start = fh.tell()
        self.data_after_tre_size = self._seg.data_size - (self.data_start - t)
        if(self.data_after_tre_size != 0):
            if(not self.data_after_allowed):
                raise RuntimeError("DES %s TRE length was expected to be %d but was actually %d" % (self.des_tag, self._seg.data_size, (self.data_start - t)))
            if(self.data_copy):
                self.data_to_copy = fh.read(self.data_after_tre_size)
            else:
                fh.seek(self.data_after_tre_size, 1)
        return True
        
    def write_to_file(self, fh):
        _FieldStruct.write_to_file(self, fh)
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
        try:
            maxlen = max(len(f.field_name) for f in self.field_value_list
                         if not isinstance(f, _FieldLoopStruct) and
                         f.field_name is not None)
        except ValueError:
            # We have no _FieldValue, so just set maxlen to a fixed value
            maxlen = 10
        res = io.StringIO()
        self.str_hook(res)
        if(self.user_subheader):
            print("User-Defined Subheader: ", file=res)
            print(self.user_subheader, file=res)
        for f in self.field_value_list:
            if(not isinstance(f, _FieldLoopStruct)):
                if(f.field_name is not None):
                    print(f.field_name.ljust(maxlen) + ": " + f.get_print(self,()),
                          file=res)
            else:
                print(f.desc(self), file=res, end='')
        if(self.data_after_tre_size and self.data_after_tre_size != 0):
            print("Extra data of length %d" % self.data_after_tre_size,
                  file=res)
        return res.getvalue()

class NitfDesObjectHandle(NitfDes):
    '''This is a class where the DES is handled by an object type
    des_implementation_class in des_implementation_field. This
    possibly also include user defined subheaders.  See for example
    DesCSATTB in geocal.

    Note that although you can directly create a class based on this one,
    there is also the create_nitf_des_structure function that automates 
    creating this from a table like we do with TREs.
    '''
    def __init__(self, seg=None):
        if(DEBUG):
            print("In constructor for %s" % self.des_tag)
        super().__init__(seg)
        
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
        res = io.StringIO()
        self.str_hook(res)
        if(self.user_subheader):
            print("User-Defined Subheader: ", file=res)
            print(self.user_subheader, file=res)
        print("Object associated with DES:", file=res)
        print(getattr(self, self.des_implementation_field), file=res)
        return res.getvalue()

# TODO May want to rework this, not sure if having handle_diff in the
# object is the right way to handle this.

class DesObjectDiff(NitfDiffHandle):
    '''Compare two NitfDesObjectHandle.'''
    def handle_diff(self, des1, des2, nitf_diff):
        if(not isinstance(des1, NitfDesObjectHandle) or
           not isinstance(des2, NitfDesObjectHandle)):
            return (False, None)
        return (True, des1.handle_diff(des2))

NitfDiffHandleSet.add_default_handle(DesObjectDiff())
    
class NitfDesCopy(NitfDes):
    '''Implementation that reads from one file and just copies to the other.
    Not normally registered, but can be useful to use for some test cases (e.g.
    want to copy over an unimplemented DES)'''
    def __init__(self, seg=None):
        super().__init__(seg)
        self.data = None

    def __str__(self):
        return "NitfDesCopy %d bytes of data" % (len(self.data))
        
    def read_from_file(self, fh, seg_index=None, nitf_literal = False):
        self.data = fh.read(self._seg.data_size)
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
        self.data = fh.read(self._seg.data_size)
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
    
def create_nitf_des_structure(name, desc_data, desc_uh = None, hlp = None,
                              des_implementation_field=None,
                              des_implementation_class=None,
                              data_after_allowed=False,
                              data_copy=False):
    '''This is like create_nitf_field_structure, but adds a little
    extra structure for DESs.

    Note that this create DES that fit into the NitfDesFieldStruct or
    NitfDesObjectHandle format (e.g., DesCSATTB). Not every DES has
    this form, see for example DesEXT_DEF_CONTENT. Classes that don't
    fit this form will generally derive from NitfDes, and will not
    call this particular function.

    This creates two classes, one that handles the overall DES, and one
    that handles the extra user subheader that might be present. If desc_uh 
    is None, then the second subheader will just returned as None. 

    This function does not register the DES class, you should also call
    NitfSegmentDataHandleSet.add_default_handle to have the DES used 
    by NitfFile.

    Note that it is perfectly fine to call create_nitf_des_structure 
    from outside of the nitf module. This can be useful for projects that
    need to support specialized DESs that aren't included in this package.
    Just call create_nitf_des_structure to add your DESs.

    '''

    # 1. First create Des class
    t = _create_nitf_field_structure()
    d = copy.deepcopy(desc_data)
    des_tag = d.pop(0)
    if((des_implementation_field and not des_implementation_class) or
       (not des_implementation_field and des_implementation_class)):
        raise RuntimeError("Need to supply either none or both of des_implementation_class and des_implementation_field")
    if(des_implementation_field):
        res = type(name, (NitfDesObjectHandle,), {})
        res.des_implementation_class = des_implementation_class
        res.des_implementation_field = des_implementation_field
        # Forward all the fields to be handled by the implementation object
        for field in t.process(d)["field_map"].keys():
            setattr(res, field, _create_attribute_forward_to_implementation_object(field))
    else:
        res = type(name, (NitfDesFieldStruct,), t.process(d))
        res.data_after_allowed = data_after_allowed
        res.data_copy = data_copy
    res.des_tag = des_tag

    # Stash description, to make available if we want to later override a DES
    # (see geocal_nitf_des.py in geocal for an example)
    res._desc_data = desc_data

    if(hlp is not None):
        try:
            # This doesn't work in python 2.7, we can't write to the
            # doc. Rather than try to do something clever, just punt and
            # skip adding help for python 2.7. This works find with python 3
            res.__doc__ = hlp
        except AttributeError:
            pass

    # 2. Then create User-defined subheader class
    res2 = None
    if (desc_uh is not None):
        t2 = _create_nitf_field_structure()
        res2 = type(name+'_UH', (_FieldStruct,), t2.process(desc_uh))
        res.uh_class = res2
    res._desc_uh = desc_uh

    return (res, res2)

NitfSegmentDataHandleSet.add_default_handle(TreOverflow)
# Don't normally use, but you can add this if desired
#NitfSegmentDataHandleSet.add_default_handle(NitfDesCopy, priority_order=-999)

__all__ = [ "NitfDesCopy", "TreOverflow", "create_nitf_des_structure"]

