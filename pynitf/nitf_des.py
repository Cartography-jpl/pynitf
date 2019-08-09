# We import a number of "private" classes from nitf_field. This module really
# is part of nitf_field.py, we have just pulled it out into a separate file
# to keep things clean
#
# Note when importing TREs that much of the documentation is in PDF tables.
# You can't easily paste this directly to emacs. But you can import to Excel.
# To do this, cut and paste the table into *Word*, and then cut and paste
# from word to Excel. For some reason, you can't go directly to Excel. You
# can then cut and paste from excel to emacs
from __future__ import print_function
from .nitf_field import FieldData, _FieldStruct, _FieldLoopStruct, \
    _FieldValueArrayAccess, _create_nitf_field_structure, create_nitf_field_structure
from .nitf_des_subheader import NitfDesSubheader
import copy
import io,six
import abc
import collections

DEBUG = False

class NitfDesCannotHandle(RuntimeError):
    '''Exception that indicates we can't read a particular Des. Note that
    this does *not* mean an error occured - e.g., a corrupt Des. Rather this
    means that the Des is a type we don't handle'''
    def __init__(self, msg = "Can't handle this type of des"):
        RuntimeError.__init__(self, msg)

@six.add_metaclass(abc.ABCMeta)
class NitfDes(object):
    '''This contains a DES that we want to read or write from NITF.
    
    This class supplies a basic interface, a specific type of DES can
    derive from this class and supply some of the missing functionality.

    We take in the DES subheader (a NitfDesSubheader object), derived classes
    should fill in details of the subheader as needed.

    We also take a class to use for the user defined subheader, if any. 
    Not all DESs have user defined subheaders, but for those that do we
    include this (e.g., CSATTB).

    A DES doesn't actually have to derive from NitfDesa if for some
    reason that is inconvenient, we use the standard duck typing and
    any class that supplies the right functions can be used. But this
    base class supplies what the interface should be.

    Note that a NitfDes class doesn't need to handle all types of DES. If 
    it can't handle reading a particular DES, it should throw a 
    NitfDesCannotHandle exception. The NitfDesSegment class will then just 
    move on to next possible handler class.
    '''
    def __init__(self, des_id=None,
                 des_subheader=None, header_size=None, data_size=None,
                 user_subheader=None,
                 user_subheader_class=None):
        if(des_subheader is not None):
            self.des_subheader = des_subheader
        else:
            h = NitfDesSubheader()
            if(des_id is not None):
                h.desid = des_id
            h.dsver = 1
            h.dsclas = "U"
            self.des_subheader = h
        self.header_size = header_size
        self.data_size = data_size
        self.user_subheader_class = user_subheader_class
        self.user_subheader = user_subheader
        if(self.user_subheader is None and
           self.user_subheader_class is not None):
            self.user_subheader = self.user_subheader_class()
        
        # Derived classes should fill in information.

    def str_hook(self, file):
        '''Convenient to have a place to add stuff in __str__ for derived
        classes. This gets called after the DES name is written, but before
        any fields. Default is to do nothing, but derived classes can 
        override this if desired.'''
        print('NitfDes', file=fh)

    # Derived classes may want to override this to give a more detailed
    # description of what kind of image this is.
    def __str__(self):
        fh = six.StringIO()
        self.str_hook(fh)
        if(self.user_subheader):
            print("User-Defined Subheader: ", file=fh)
            print(self.user_subheader, file=fh)
        return fh.getvalue()

    def read_user_subheader(self):
        '''Helper function to read the user subheader. For use in derived
        class read_from_file function. This should be called after the 
        subheader has already been filled in.'''
        if(self.des_subheader.desshl == 0 and
           self.user_subheader_class is not None):
            raise RuntimeError("The expected user defined subheader was not found")
        if(self.des_subheader.desshl > 0):
            fh = six.BytesIO(self.des_subheader.desshf)
            self.user_subheader.read_from_file(fh)

    def write_user_subheader(self, sh):
        '''This writes the user subheader section of the des subheader. Note
        that derived classes do not normally call this function. Because the
        subheader is written before write_to_file is called, we can't call this
        in that function (unlike read_from_file). Instead, the NitfDesSegment
        class calls this function.'''
        if(self.user_subheader_class):
            fh = six.BytesIO()
            self.user_subheader.write_to_file(fh)
            sh.desshf = fh.getvalue()
        else:
            sh.desshf = ""
            
    @abc.abstractmethod
    def read_from_file(self, fh):
        '''Read an DES from a file. For larger DES a derived class might
        want to not actually read in the data (e.g., you might memory
        map the data or otherwise generate a 'read on demand'), but at
        the end of the read fh should point past the end of the DES data
        (e.g., do a fh.seek(start_pos + size of DES) or something like 
        that).

        This should also handle the reading of the user defined subheader.
        '''
        self.read_user_subheader()
        raise NotImplementedError()

    @abc.abstractmethod
    def write_to_file(self, fh):
        '''Write an DES to a file.'''
        raise NotImplementedError()
    
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
    uh_class = None
    des_tag = None
    data_after_allowed = None
    def __init__(self, des_subheader=None, header_size=None,
                 user_subheader=None, data_size=None):
        NitfDes.__init__(self, self.__class__.des_tag,
                         des_subheader, header_size, data_size,
                         user_subheader = user_subheader,
                         user_subheader_class = self.__class__.uh_class)
        _FieldStruct.__init__(self)
        if(self.des_subheader.desid != self.__class__.des_tag):
            raise NitfDesCannotHandle()
        self.data_start = None
        self.data_after_tre_size = None
        
    def read_from_file(self, fh, nitf_literal = False):
        self.read_user_subheader()
        t = fh.tell()
        _FieldStruct.read_from_file(self,fh, nitf_literal)
        self.data_start = fh.tell()
        self.data_after_tre_size = self.data_size - (self.data_start - t)
        if(self.data_after_tre_size != 0):
            if(not self.data_after_allowed):
                raise RuntimeError("DES %s TRE length was expected to be %d but was actually %d" % (self.des_tag, self.data_size, (self.data_start - t)))
            fh.seek(self.data_after_tre_size, 1)
        
    def write_to_file(self, fh):
        _FieldStruct.write_to_file(self, fh)
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
        res = six.StringIO()
        self.str_hook(res)
        for f in self.field_value_list:
            if(not isinstance(f, _FieldLoopStruct)):
                if(f.field_name is not None):
                    print(f.field_name.ljust(maxlen) + ": " + f.get_print(self,()),
                          file=res)
            else:
                print(f.desc(self), file=res, end='')
        return res.getvalue()

    def summary(self):
        res = six.StringIO()
        #print("TRE - %s" % self.tre_tag, file=res)

class NitfDesObjectHandle(NitfDes):
    '''This is a class where the DES is handled by an object type
    des_implementation_class in des_implementation_field. This
    possibly also include user defined subheaders.  See for example
    DesCSATTB in geocal.

    Note that although you can directly create a class based on this one,
    there is also the create_nitf_des_structure function that automates 
    creating this from a table like we do with TREs.
    '''
    uh_class = None
    des_tag = None
    def __init__(self, des_subheader=None, header_size=None,
                 user_subheader=None, data_size=None):
        if(DEBUG):
            print("In constructor for %s" % self.__class__.des_tag)
        NitfDes.__init__(self, self.__class__.des_tag,
                         des_subheader, header_size, data_size,
                         user_subheader = user_subheader,
                         user_subheader_class = self.__class__.uh_class)
        if(DEBUG):
            print("Trying to match %s" % self.des_subheader.desid)
        if(self.des_subheader.desid != self.__class__.des_tag):
            if(DEBUG):
                print("Match failed")
            raise NitfDesCannotHandle()
        if(DEBUG):
            print("Match succeeded in constructor")
        
    def read_from_file(self, fh):
        self.read_user_subheader()
        setattr(self, self.des_implementation_field,
                self.des_implementation_class.des_read(fh))
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
        res = six.StringIO()
        self.str_hook(res)
        print("Object associated with DES:", file=res)
        print(getattr(self, self.des_implementation_field), file=res)
        return res.getvalue()

    def summary(self):
        res = six.StringIO()
        #print("TRE - %s" % self.tre_tag, file=res)
        
class NitfDesPlaceHolder(NitfDes):
    '''Implementation that doesn't actually read any data, useful as a
    final place holder if none of our other NitfDes classes can handle
    a particular DES. We just skip over the data when reading.'''
    def __init__(self, des_subheader=None, header_size=None, data_size=None):
        NitfDes.__init__(self,"",des_subheader, header_size, data_size)
        self.data_start = None

    def __str__(self):
        return "NitfDesPlaceHolder %d bytes of data" % (self.data_size)
        
    def read_from_file(self, fh, nitf_literal = False):
        self.data_start = fh.tell()
        fh.seek(self.data_size, 1)

    def write_to_file(self, fh):
        '''Write an DES to a file.'''
        raise NotImplementedError("Can't write a NitfDesPlaceHolder")

class TreOverflow(NitfDes):
    '''DES used to handle TRE overflow.'''
    def __init__(self, des_subheader=None, header_size=None, data_size=None,
                 seg_index=None, overflow=None):
        NitfDes.__init__(self, "TRE_OVERFLOW", des_subheader,
                         header_size, data_size)
        if(self.des_subheader.desid.encode("utf-8") != b'TRE_OVERFLOW'):
            raise NitfDesCannotHandle()
        if(des_subheader is None):
            self.des_subheader.desoflw = str.upper(overflow)
            self.des_subheader.desitem = seg_index
        self.data = None

    def read_from_file(self, fh):
        '''Read an DES from a file.'''
        self.data = fh.read(self.data_size)

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
                              data_after_allowed=False):
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
    des_register_class to have the DES used by NitfFile.

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

class NitfDesHandleList(object):
    '''Small class to handle to list of DES objects. This is little more
    complicated than just a list of handlers. The extra piece is allowing
    a priority_order to be assigned to the handlers, we look for 
    lower number first. So for example we can put NitfDesPlaceHolder as the
    highest number, and it will be tried after all the other handlers have
    been tried.

    This is a chain-of-responsibility pattern, with the addition of an
    ordering based on a priority_order. 
    '''
    def __init__(self):
        self.handle_list = collections.defaultdict(lambda : set())

    def add_handle(self, cls, priority_order=0):
        self.handle_list[priority_order].add(cls)

    def discard_handle(self, cls):
        '''Discard any handle of the given class. Ok if this isn't actually
        in the list of handles.'''
        for k in sorted(self.handle_list.keys()):
            self.handle_list[k].discard(cls)

    def des_handle(self, subheader, header_size, data_size, fh):
        for k in sorted(self.handle_list.keys()):
            for cls in self.handle_list[k]:
                try:
                    t = cls(des_subheader=subheader,
                            header_size=header_size,
                            data_size=data_size)
                    t.read_from_file(fh)
                    return t
                except NitfDesCannotHandle:
                    pass
        raise NitfDesCannotHandle("No handle found for data.")

_hlist = NitfDesHandleList()


def nitf_des_read(subheader, header_size, data_size, fh):
    return _hlist.des_handle(subheader, header_size, data_size, fh)

def register_des_class(cls, priority_order=0):
    _hlist.add_handle(cls, priority_order)

def unregister_des_class(cls):
    '''Remove a handler from the list. This isn't used all that often,
    but it can be useful in testing.'''
    _hlist.discard_handle(cls)
    
register_des_class(TreOverflow)
register_des_class(NitfDesPlaceHolder, priority_order=1000)

__all__ = [ "NitfDesCannotHandle", "NitfDes", "NitfDesPlaceHolder",
            "TreOverflow", "create_nitf_des_structure",
            "nitf_des_read", "register_des_class", "unregister_des_class"]

