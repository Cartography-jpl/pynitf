# We import a number of "private" classes from nitf_field. This module really
# is part of nitf_field.py, we have just pulled it out into a separate file
# to keep things clean
#
# Note when importing TREs that much of the documentation is in PDF tables.
# You can't easily paste this directly to emacs. But you can import to Excel.
# To do this, cute and paste the table into *Word*, and then cut and paste
# from word to Excel. For some reason, you can't go directly to Excel. You
# can then cut and paste from excel to emacs
from __future__ import print_function
from .nitf_field import _FieldStruct, _FieldLoopStruct, \
    _FieldValueArrayAccess, _create_nitf_field_structure
from .nitf_des_subheader import des_desc
import copy
import io,six

class Des(_FieldStruct):
    def des_bytes(self):
        '''All of the TRE expect for the front two cetag and cel fields'''
        fh = six.BytesIO()
        _FieldStruct.write_to_file(self, fh)
        return fh.getvalue()
    def read_from_des_bytes(self, bt, nitf_literal = False):
        fh = six.BytesIO(bt)
        _FieldStruct.read_from_file(self,fh, nitf_literal)
    def read_from_file(self, fh, nitf_literal = False):
        _FieldStruct.read_from_file(self,fh, nitf_literal)
    def write_to_file(self, fh):
        t = self.des_bytes()
        fh.write(t)
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

class DesUnknown(Des):
    '''The is a general class to handle DESs that we don't have another 
    handler for. It just reports the tre string.'''
    def __init__(self, name):
        self.name = name
        super(DesUnknown, self).__init__()
        
    def read_from_file(self, fh, nitf_literal = False):
        # Nothing to do, we can just ignore the data
        pass

    def __str__(self):
        '''Text description of structure, e.g., something you can print
        out.'''
        res = six.StringIO()
        print("   Unknown DES: %s" % self.name)
        return res.getvalue()

class TreOverflow(Des):
    '''DES used to handle TRE overflow.'''
    def __init__(self):
        pass
    def __str__(self):
        '''Text description of structure, e.g., something you can print
        out.'''
        res = six.StringIO()
        print( "   String: %s" % self.des_bytes, file=res)
        return res.getvalue()

_des_class = {}

def des_object(des_name):
    '''Return a DES object that can be used to read or write the given tre
    name, or a TreUnknown if we don't have that registered.'''
    if(des_name in _des_class):
        return _des_class[des_name]()
    return DesUnknown(des_name)
    
def read_des_data(desid, data):
    '''Read a blob of data, and translate into a DES'''
    fh = six.BytesIO(data)
    t = des_object(desid)
    t.read_from_file(fh)
    return t

def create_nitf_des_structure(name, description, hlp = None):
    '''This is like create_nitf_field_structure, but adds a little
    extra structure for DESs. It basically creates a class out 

    Note that it is perfectly fine to call create_nitf_field_structure 
    from outside of the nitf module. This can be useful for projects that
    need to support specialized TREs that aren't included in this package.
    Just call create_nitf_field_structure to add your TREs.

    '''

    t = _create_nitf_field_structure()
    des_tag = description.pop(0)
    d = des_desc + description
    res = type(name, (Des,), t.process(d))
    res.des_tag = des_tag

    # Stash description, to make available if we want to later override a TRE
    # (see geocal_nitf_rsm.py in geocal for an example)
    #res._description = description

    if(hlp is not None):
        try:
            # This doesn't work in python 2.7, we can't write to the
            # doc. Rather than try to do something clever, just punt and
            # skip adding help for python 2.7. This works find with python 3
            res.__doc__ = hlp
        except AttributeError:
            pass
    _des_class[des_tag.encode("utf-8")] = res
    return res

_des_class[b'TRE_OVERFLOW'] = TreOverflow
__all__ = [ "TreOverflow", "Des", "DesUnknown", "des_object", "read_des_data",
            "create_nitf_des_structure"]

