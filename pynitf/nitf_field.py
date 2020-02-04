# The code in this class is used to handle a NITF field structure, e.g., a file
# header or a TRE.
#
# The class structure is a little complicated, so you can look and the UML
# file doc/Nitf_file.xmi (e.g., use umbrello) to see the design.
#
# As an external user, the main thing that is exported is
# create_nitf_field_structure, The created class has functions to read
# and write each of the NITF fields,
# a write_to_file and read_from_file function, and a __str__() to give a
# printable description of the contents of the structure.
#
# A few support classes/routines are also exported. This includes
# NitfLiteral, FieldData (for things like TREs), hardcoded_value, and
# hardcoded_value1
#
# Note what might be slightly confusing using these classes, we do all this
# to setup a NitfField class, not a particular object. These means that all
# the variables internal to for instance _FieldValueAccess are at the
# class level of something like NitfFileHeader, so two objects ob1, ob2 will
# have the exact same _FieldValueAccess. This is accounted for in the
# existing code, but if you are modifying these classes you should be aware
# of this. There is a note in each class if it __dict__ is class or object
# level. Of course __dict__ is that object level for each class, the question
# is if we have one object for all _FieldStruct objects, or if the objects
# are per _FieldStruct.

import copy
import io
from collections import defaultdict
import sys
from struct import *
import logging
import itertools
import operator
import functools
import math
from .nitf_diff_handle import NitfDiffHandle

# Add a bunch of debugging if you are diagnosing a problem
DEBUG = False
class FieldValueArray(object):
    '''Provides an array access to a _FieldValue that is part of a loop 
    structure.

    This provides an array like interface, so you can get an set values
    with things like a[0,1]. We do *not* support slices. The arrays in NITF
    are in general "ragged" arrays, so for example it might be something
    like [[1,2], [3,4,5]] where the first row has 2 columns, the second row
    has three columns. It isn't exactly clear how to handle slices, so we
    just don't do that.

    In addition, you can use "to_list()" to convert an array to a nested list
    of values.'''
    # The __dict__ is at object level
    def __init__(self, fv, parent_obj):
        self.fv=fv
        self.parent_obj = parent_obj
    def __getitem__(self, ind):
        if(isinstance(ind, tuple)):
            return self.fv.get(self.parent_obj, ind)
        else:
            return self.fv.get(self.parent_obj, (ind,))
    def __setitem__(self,ind,v):
        if(isinstance(ind, tuple)):
            self.fv.set(self.parent_obj, ind,v)
        else:
            self.fv.set(self.parent_obj, (ind,),v)
    def to_list(self, lead=()):
        '''Return the data as a nested list.'''
        if(len(lead) == self.dim_size() - 1):
            return [self[(*lead, i)] for i in range(self.shape(lead))]
        return [self.to_list(lead=(*lead, i)) for i in range(self.shape(lead))]
    def dim_size(self):
        '''Shortcut for getting the length of the looping size (i.e., is
        this a 1d, 2d or 3d object).'''
        return len(self.fv.loop.size)
    def shape(self, lead=()):
        '''Shortcut for calling shape in the looping structure for this
        array'''
        return self.fv.loop.shape(self.parent_obj, lead)
    def type(self):
        return self.fv.ty
    def values(self, lead=()):
        '''Iterate through values. This uses the 'C' like order, where we
        vary the last. This is like doing a flatten on the results of 
        to_list'''
        if(self.shape(lead=lead) is not None):
            if(len(lead) == self.dim_size() - 1):
                for i in range(self.shape(lead=lead)):
                    yield self[(*lead,i)]
            else:
                for i in range(self.shape(lead=lead)):
                    for j in self.values(lead=(*lead,i)):
                        yield j
    def items(self,lead=()):
        '''Likes values(), but iterator through a tuple of the (index,value)
        instead of just values.'''
        if(self.shape(lead=lead) is not None):
            if(len(lead) == self.dim_size() - 1):
                for i in range(self.shape(lead=lead)):
                    yield ((*lead,i), self[(*lead,i)])
            else:
                for i in range(self.shape(lead=lead)):
                    for j in self.items(lead=(*lead,i)):
                        yield j
    @classmethod
    def is_shape_equal(cls, arr1, arr2, lead=()):
        '''Return True if the shape of arr1 and arr2 are the same,
        False otherwise'''
        if(arr1.dim_size() != arr2.dim_size()):
            return False
        if(len(lead) == arr1.dim_size() - 1):
            return arr1.shape(lead=lead) == arr2.shape(lead=lead)
        if(arr1.shape(lead=lead) is not None):
            for i in range(arr1.shape(lead=lead)):
                if not cls.is_shape_equal(arr1, arr2, lead=(*lead,i)):
                    return False
        return True

class _FieldValueAccess(object):
    '''Python descriptor to provide access for getting and setting a
    single field value.'''
    # The __dict__ is at class level
    def __init__(self, fv):
        self.fv = fv
    def __get__(self, parent_obj, cls):
        if(self.fv.loop is not None):
            return FieldValueArray(self.fv, parent_obj)
        return self.fv.get(parent_obj, ())
    def __set__(self, parent_obj, v):
        if(self.fv.loop is not None):
            raise RuntimeError("Need to give indexes to set value for field "
                               + self.fv.field_name)
        self.fv.set(parent_obj, (), v)

def float_to_fixed_width(n, max_width, maximum_precision=False):
    '''Utility function that tries to fit a float with maximum precision into
    other a fixed point string, or optionally an exponent string'''
    s1 = '{:.{}f}'
    if(maximum_precision and
       (n < pow(10,-max_width+5) or
        n > pow(10,max_width-5))):
        s1 = '{:.{}e}'
    for i in range(max_width - 2, -1, -1):
        s = s1.format(n, i)
        if len(s) <= max_width:
            break
    if(len(s) > max_width):
        raise RuntimeError("Can't fit %f into length %d" % (n, max_width))
    return s
        
class _FieldValue(object):
    '''This handles a single NITF field. We consider a field in a looping 
    structure to be a single field presented as an array. So for example
    LISH0, LISH1,...LISH5 is one field 'lish' that is an array size 6.
    '''
    # The __dict__ is at class level
    def __init__(self, field_name, size, ty, loop, options):
        '''Give the size, type, loop structure, and options to to use. If
        default is given as None, we use a default default value of
        all spaces for type 'str' or 0 for type int or float.
        '''
        self.field_name = field_name
        self.size = size
        self.ty = ty
        self.loop = loop
        # The format string fstring is used to add the proper padding to give
        # the full size. For string is padded with spaces on the left. For
        # integers we pad on the right with 0.
        self.fstring = "{:%ds}" % self.size
        self.frmt = "%s"
        if(ty == int):
            self.fstring = "{:s}"
            self.frmt = "%%0%dd" % self.size
        if(ty == float):
            self.fstring = "{:%ds}" % self.size
            self.frmt = lambda v : float_to_fixed_width(v, self.size)
        if("frmt" in options):
            self.frmt = options["frmt"]
        self.default = options.get("default", None)
        self.condition = options.get("condition", None)
        self.optional = options.get("optional", False)
        self.optional_char = options.get("optional_char", " ")

    def value(self,parent_obj):
        if(self.field_name is None):
            return ''
        if(self.field_name not in parent_obj.value):
            if(self.default is not None):
                parent_obj.value[self.field_name] = defaultdict(lambda : self.default)
            elif(self.optional):
                parent_obj.value[self.field_name] = defaultdict(lambda : None)
            elif(self.ty == str):
                parent_obj.value[self.field_name] = defaultdict(lambda : " " * self.size)
            else:
                parent_obj.value[self.field_name] = defaultdict(lambda : 0)
        return parent_obj.value[self.field_name]
    def get_print(self, parent_obj, key):
        '''Return string suitable for printing. This is either the 
        value of this field, or "Not used" if the condition isn't met.'''
        t = self.get(parent_obj,key)
        if(t is None):
            t = "Not used"
        return str(t)
    def check_condition(self, parent_obj, key):
        '''Evaluate the condition (if present) and return False if it isn't
        met, True if it is or if there is no condition'''
        if(self.condition is None):
            return True
        f = parent_obj
        if(len(key) > 0):
            i1 = key[0]
        if(len(key) > 1):
            i2 = key[1]
        if(len(key) > 2):
            i3 = key[2]
        if(len(key) > 3):
            i4 = key[3]
        if(DEBUG):
            print("Condition: " + self.condition)
            print("eval: " + str(eval(self.condition)))
        #print("Condition: " + self.condition)
        #print(f.existence_mask)
        #print("eval: " + str(eval(self.condition)))
        return eval(self.condition)
    def get(self,parent_obj,key, no_type_conversion=False):
        if(self.field_name is None):
            return ''
        if(self.loop is not None):
            self.loop.check_index(parent_obj, key)
        if(not self.check_condition(parent_obj, key)):
            return None
        try:
            v = None
            if(hasattr(parent_obj, self.field_name + "_value")):
                if(self.loop is None):
                    return getattr(parent_obj, self.field_name + "_value")()
                else:
                    return getattr(parent_obj, self.field_name + "_value")(*key)
            v = self.value(parent_obj)[key]
            if(self.optional and v is None):
                return None
            if(no_type_conversion):
                return v
            if(isinstance(v, NitfLiteral)):
                v = v.value
            if(self.ty == str):
                return self.ty(v).rstrip()
            else:
                return self.ty(v)
        except Exception as e:
            if sys.version_info > (3,):
                if(self.loop is None):
                    raise RuntimeError("Error occurred getting '%s' from '%s'. Value '%s'" % (self.field_name, type(parent_obj).__name__, v)) from e
                else:
                    raise RuntimeError("Error occurred getting '%s[%s]' from '%s'. Value '%s'" % (self.field_name, key, type(parent_obj).__name__, v)) from e
            else:
                raise
    def set(self,parent_obj,key,v):
        if(self.field_name is None):
            raise RuntimeError("Can't set a reserved field")
        if(self.loop is not None):
            self.loop.check_index(parent_obj, key)
        if(not self.check_condition(parent_obj, key)):
            raise RuntimeError("Can't set value for field %s because the condition '%s' isn't met" % (self.field_name, self.condition))
        if(hasattr(parent_obj, self.field_name + "_value")):
            raise RuntimeError("Can't set value for field " + self.field_name)
        # If we are implementing the TRE in its own object, don't allow
        # the raw values to be set
        if(hasattr(parent_obj, "tre_implementation_field")):
            raise RuntimeError("You can't directly set fields in %s TRE. Instead, set this through the %s object" % (parent_obj.cetag_value(), parent_obj.tre_implementation_field))
        if(v is None and not self.optional):
            raise RuntimeError("Can only set a field to 'None' if it is marked as being optional")
        self.value(parent_obj)[key] = v
    def bytes(self, parent_obj, key=()):
        '''Return bytes version of this value, formatted and padded as
        NITF will store this.'''
        # If we have a NitfLiteral we assume some sort of funky formating
        # that is handled outside of this class. Pad, but otherwise don't
        # process this.
        t = self.get(parent_obj, key, no_type_conversion=True)
        if(isinstance(t, NitfLiteral)):
            t = ("{:%ds}" % self.size).format(t.value)
        elif(t is None and self.optional):
            t = ("{:%ds}" % self.size).format("").replace(" ", self.optional_char)
        else:
            # Otherwise, get the value and do the formatting that has been
            # supplied to us.
            v = self.get(parent_obj, key)
            # Don't format bytes if we have python 3
            if sys.version_info > (3,) and self.ty == bytes:
                t = v
            elif(isinstance(self.frmt, str)):
                t = self.fstring.format(self.frmt % v)
            else:
                t = self.fstring.format(self.frmt(v))
        if(len(t) != self.size):
            raise RuntimeError("Formatting error. String '%s' is not right length for NITF field %s" % (t, self.field_name))
        if(self.ty == bytes):
            return t
        else:
            return t.encode("utf-8")
    def write_to_file(self, parent_obj, key, fh):
        if(not self.check_condition(parent_obj, key)):
            return
        if(self.field_name is not None):
            if(DEBUG):
                print("Writing: ", self.field_name, self.bytes(parent_obj,key))
            parent_obj.fh_loc[self.field_name][key] = fh.tell()
        fh.write(self.bytes(parent_obj,key))
    def update_file(self, parent_obj, key, fh):
        '''Rewrite to a file after the value of this field has been updated'''
        # Not sure if updating a field that doesn't meet the condition should
        # just be a noop, or an error. For now treat as an error but we can
        # change this behavior is needed.
        if(not self.check_condition(parent_obj, key)):
            raise RuntimeError("Can't update value for field %s because the condition '%s' isn't met" % (self.field_name, self.condition))
        if(DEBUG):
            print("Updating: ", self.field_name)
        last_pos = fh.tell()
        fh.seek(parent_obj.fh_loc[self.field_name][key])
        fh.write(self.bytes(parent_obj,key))
        fh.seek(last_pos)           
    def read_from_file(self, parent_obj, key, fh,nitf_literal=False):
        if(not self.check_condition(parent_obj, key)):
            return
        if(DEBUG and self.field_name is not None):
            print("Reading: ", self.field_name, " bytes: ", self.size)
        t = fh.read(self.size)
        if(DEBUG and self.field_name is not None):
            print("Value: " + str(t))
        if(len(t) != self.size):
            raise RuntimeError("Not enough bytes left to read %d bytes for field %s" % (self.size, self.field_name))
        if(self.field_name is not None):
            try:
                if(nitf_literal):
                    self.value(parent_obj)[key] = NitfLiteral(t.rstrip().decode("utf-8"))
                elif(self.optional and t.rstrip(self.optional_char.encode('utf-8') + b' ') == b''):
                    self.value(parent_obj)[key] = None
                elif(self.ty == str):
                    self.value(parent_obj)[key] = t.rstrip().decode("utf-8", "replace")
                else:
                    v = t.rstrip()
                    if(v == b''):
                        raise RuntimeError("Empty string read for field %s" % self.field_name)
                    self.value(parent_obj)[key] = self.ty(v)
            except Exception as e:
                raise Exception("Exception while parsing ", self.field_name, " from ", t.rstrip(), "underlying error: ", e)

class _FieldLoopStruct(object):
    # The __dict__ is at class level
    def __init__(self, size):
        self.size = size
        # I think we only ever have 4 levels of nesting. We check for this,
        # in case we run into something else at some point. We could
        # extend this if needed, but we'll wait until we have to
        if(len(self.size) > 4):
            raise RuntimeError("We only support 4 levels of nesting now")
        self.field_value_list = []
    def shape(self, parent_object, lead=()):
        f = parent_object
        if(len(lead) >= 1):
            i1 = lead[0]
        if(len(lead) >= 2):
            i2 = lead[1]
        if(len(lead) >= 3):
            i3 = lead[2]
        return eval(self.size[len(lead)])
    def write_to_file(self, parent_object, key, fh):
        if(key is None):
            lead = ()
        else:
            lead = key
        maxi = self.shape(parent_object, lead=lead)
        # Treat missing data because of a failed condition as size 0
        if(maxi is None):
            maxi = 0
        for i in range(maxi):
            for f in self.field_value_list:
                f.write_to_file(parent_object, lead + (i,), fh)
    def read_from_file(self, parent_object, key, fh, nitf_literal=False):
        if(key is None):
            lead = ()
        else:
            lead = key
        maxi = self.shape(parent_object, lead=lead)
        # Treat missing data because of a failed condition as size 0
        if(maxi is None):
            maxi = 0
        for i in range(maxi):
            for f in self.field_value_list:
                f.read_from_file(parent_object, lead + (i,), fh, nitf_literal)
    def field_names(self):
        '''Return a iterator of all field names in this structure (or loops
        nested in this structure).
        '''
        for f in self.field_value_list:
            if(not isinstance(f, _FieldLoopStruct)):
                if(f.field_name is not None):
                    yield f.field_name
            else:
                for fname in f.field_names():
                    yield fname
    def desc(self, parent_object):
        '''Text description of structure, e.g., something you can print
        out.'''
        try:
            maxlen = max(len(f.field_name) for f in self.field_value_list
                         if not isinstance(f, _FieldLoopStruct) and
                         f.field_name is not None)
        except ValueError:
            # We have no _FieldValue, so just set maxlen to a fixed value
            maxlen = 10
        maxi1 = self.shape(parent_object)
        maxlen += 2 + len(str(maxi1))
        res = io.StringIO()
        lead = "  " * (len(self.size) - 1)
        print(lead + "Loop - " + self.size[-1], file=res)
        for f in self.field_value_list:
            if(not isinstance(f, _FieldLoopStruct)):
                if(f.field_name is None):
                    pass
                elif(len(self.size) == 1):
                    if(maxi1 is None):
                        maxi1=0
                    for i1 in range(maxi1):
                        print(lead + "  " +
                              ("%s[%d]" % (f.field_name, i1)).ljust(maxlen) +
                              ": " + f.get_print(parent_object,(i1,)),
                              file=res)
                elif(len(self.size) == 2):
                    if(maxi1 is None):
                        maxi1=0
                    for i1 in range(maxi1):
                        maxi2 = self.shape(parent_object,lead=(i1,))
                        for i2 in range(maxi2):
                            print(lead + "  " +
                                  ("%s[%d, %d]" % (f.field_name, i1, i2)).ljust(maxlen) +
                                  ": " +  f.get_print(parent_object,(i1,i2)),
                                  file=res)
                elif(len(self.size) == 3):
                    if(maxi1 is None):
                        maxi1=0
                    for i1 in range(maxi1):
                        maxi2 = self.shape(parent_object,lead=(i1,))
                        if(maxi2 is None):
                            maxi2 = 0
                        for i2 in range(maxi2):
                            maxi3 = self.shape(parent_object,lead=(i1,i2))
                            if(maxi3 is None):
                                maxi3 = 0
                            for i3 in range(maxi3):
                                print(lead + "  " +
                                      ("%s[%d, %d, %d]" % (f.field_name, i1, i2, i3)).ljust(maxlen) +
                                      ": " +  f.get_print(parent_object,(i1,i2, i3)),
                                      file=res)
                elif(len(self.size) == 4):
                    if(maxi1 is None):
                        maxi1=0
                    for i1 in range(maxi1):
                        maxi2 = self.shape(parent_object,lead=(i1,))
                        if(maxi2 is None):
                            maxi2 = 0
                        for i2 in range(maxi2):
                            maxi3 = self.shape(parent_object,lead=(i1,i2))
                            if(maxi3 is None):
                                maxi3 = 0
                            for i3 in range(maxi3):
                                maxi4 = self.shape(parent_object,lead=(i1,i2, i3))
                                if(maxi4 is None):
                                    maxi4 = 0
                                for i4 in range(maxi4):
                                    print(lead + "  " +
                                          ("%s[%d, %d, %d, %d]" % (f.field_name, i1, i2, i3, i4)).ljust(maxlen) +
                                      ": " +  f.get_print(parent_object,(i1,i2, i3, i4)),
                                      file=res)
            else:
                print(f.desc(parent_object), file=res)
        return res.getvalue()
        
    def check_index(self, parent_object, key):
        '''Throw a IndexError exception if key is out of range'''
        if(len(key) != len(self.size)):
            raise IndexError()
        for i in range(len(key)):
            if(key[i] < 0 or key[i] >= self.shape(parent_object, lead=key[0:i])):
                raise IndexError()
        
class _FieldStruct(object):
    # The __dict__ is at object level
    def __init__(self):
        '''Create a NITF field structure structure.'''
        self.value = {}
        self.fh_loc = defaultdict(lambda: dict())
    def items(self, array_as_list = True):
        '''Return an iterator that gives returns tuples with the field name
        and value of that field. 

        By default, for arrays/looped data we convert the data to a
        possible nested list (e.g., [1,2,3] for a field in a loop of
        size 3, [[1,2,3], [1,2]] for a field with an outer loop of
        size 2, and inner loop of (3,2).

        Note that some fields in a FieldStruct might be conditional. In all
        cases the field name is returned, even if it is conditional with
        the condition false. In the case that the conditional field isn't 
        present, its value is returned as None.

        Depending on the application, converting arrays to lists might not
        be desirable. If the array_as_list keyword is set to False we instead
        return a FieldValueArray. Note that FieldValueArray has its own 
        iterate function which can be used to step through the array (e.g.,
        in comparing 2 arrays).
        '''
        for f in self.field_value_list:
            if(not isinstance(f, _FieldLoopStruct)):
                if(f.field_name is not None):
                    yield (f.field_name, f.get(self, ()))
            else:
                for fname in f.field_names():
                    if(array_as_list):
                        yield (fname, getattr(self, fname).to_list())
                    else:
                        yield (fname, getattr(self, fname))
    def write_to_file(self, fh):
        '''Write to a file stream.'''
        for f in self.field_value_list:
            f.write_to_file(self, (), fh)
    def read_from_file(self, fh, nitf_literal=False):
        '''Read from a file stream.  
        
        nitf_literal set to True is to handle odd formatting rules,
        where we want to read the values from a file as a string and
        not apply any additional formatting. The data is read as
        NitfLiteral objects. Normally you don't want this option, but
        it can be useful for cases hard to capture otherwise (e.g.,
        heritage systems that depend on specific formatting).
        '''
        for f in self.field_value_list:
            f.read_from_file(self, (), fh, nitf_literal)
    def update_field(self, fh, field_name, value, key = ()):
        '''Update a field name in an open file'''
        fv = self.field_map[field_name]
        fv.set(self, key, value)
        fv.update_file(self, key, fh)
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
        for f in self.field_value_list:
            if(not isinstance(f, _FieldLoopStruct) and f.field_name is not None):
                print(f.field_name.ljust(maxlen) + ": " + f.get_print(self,()),
                      file=res)
            else:
                print(f.desc(self), file=res, end='')
        return res.getvalue()

    def __eq__(self, other):
        return str(self) == str(other)

class FieldData(object):
    '''Class to handle generic variable size data. We might add more
    specific classes, but for now just have this one generic one.

    There is size_field that we use to know what the field size is. There
    are two kinds of behavior when we set a value:

    1. We want to take the size of the value, and use that to fill in 
       the size_field. This is useful for example for putting TREs in a
       image header, we don't know what the size is ahead of time and just 
       want to set this.
    2. We know the size, want to hold this fixed, and trigger an error if
       we try to set a value other than this size. This is useful for
       things that are represented as binary data in a TRE, but where the
       size is know ahead of time (e.g., TreENGRDA).

    Note further that in some cases, the size is really the size of the
    data plus something else. For example, in the image header the size
    of the TRE includes both the TRE and an additional field indicating
    if we have overflow. You can supply 'size_offset' option to specify
    an offset that should be applied to the size.
    '''
    def __init__(self, field_name, size_field, ty, loop, options):
        '''Note options can contains 'size_offset' to give the offset in
        the size variable, and 'size_not_updated' which says to check the
        size of data written rather than updating size_field to whatever
        we have set'''
        self.field_name = field_name
        self.loop = loop
        self.condition = options.get("condition", None)
        self.size_offset = options.get("size_offset", 0)
        self.size_not_updated = options.get("size_not_updated", False)
        self.ty = ty
        # This isn't exactly the size. Rather it is the expression that
        # we either use to read or set the size, e.g., "ixshdl". Note
        # that in standard NITF bizarreness this isn't actually the size,
        # but rather size_offset + the size
        self.size_field = size_field
    def check_condition(self, parent_obj, key):
        '''Evaluate the condition (if present) and return False if it isn't
        met, True if it is or if there is no condition'''
        if(self.condition is None):
            return True
        f = parent_obj
        if(len(key) > 0):
            i1 = key[0]
        if(len(key) > 1):
            i2 = key[1]
        if(len(key) > 2):
            i3 = key[2]
        if(len(key) > 3):
            i4 = key[3]
        if(DEBUG):
            print("Condition: " + self.condition)
            print("eval: " + str(eval(self.condition)))
        return eval(self.condition)
    def value(self, parent_obj):
        if(self.field_name not in parent_obj.value):
            parent_obj.value[self.field_name] = defaultdict(lambda : b'')
        return parent_obj.value[self.field_name]
    def get(self,parent_obj,key):
        if(self.loop is not None):
            self.loop.check_index(parent_obj, key)
        if(not self.check_condition(parent_obj, key)):
            return None
        return self.value(parent_obj)[key]
    def set(self,parent_obj,key,v):
        if(self.loop is not None):
            self.loop.check_index(parent_obj, key)
        if(not self.check_condition(parent_obj, key)):
            raise RuntimeError("Can't set value for field %s because the condition '%s' isn't met" % (self.field_name, self.condition))
        self.value(parent_obj)[key] = v
        f = parent_obj
        if(len(key) > 0):
            i1 = key[0]
        if(len(key) > 1):
            i2 = key[1]
        if(len(key) > 2):
            i3 = key[2]
        if(len(key) > 3):
            i4 = key[3]
        if(self.size_not_updated):
            if (type(self.size_field) == int):
                sz = self.size_field
            else:
                sz = eval(self.size_field)
            if(sz != 0):
                sz -= self.size_offset
            if(len(v) != sz):
                raise RuntimeError("FieldData was expected to be exactly %d bytes, but data that we tried to set was instead %d bytes" % (sz, len(v)))
        else:
            if(len(v) == 0):
                exec("%s = 0" % self.size_field)
            else:
                exec("%s = %d" % (self.size_field, len(v) +
                                  self.size_offset))
    def write_to_file(self, parent_obj, key, fh):
        if(self.loop is not None):
            self.loop.check_index(parent_obj, key)
        if(not self.check_condition(parent_obj, key)):
            return
        # Check that size is still correct. It is possible a value was set,
        # and then we updated the size field without updating data.
        if(self.size_not_updated):
            f = parent_obj
            if(len(key) > 0):
                i1 = key[0]
            if(len(key) > 1):
                i2 = key[1]
            if(len(key) > 2):
                i3 = key[2]
            if(len(key) > 3):
                i4 = key[3]
            if (type(self.size_field) == int):
                sz = self.size_field
            else:
                sz = eval(self.size_field)
            if(sz != 0):
                sz -= self.size_offset
            lndata = len(self.value(parent_obj)[key])
            if(lndata != sz):
                raise RuntimeError("FieldData was expected to be exactly %d bytes, but data was instead %d bytes" % (sz, lndata))
        
        if(len(self.value(parent_obj)[key]) == 0):
            return
        parent_obj.fh_loc[self.field_name][key] = fh.tell()
        if(DEBUG):
            print("Writing Field Data: ", self.field_name, self.value(parent_obj)[key])
        fh.write(self.value(parent_obj)[key])
    def read_from_file(self, parent_obj, key, fh,nitf_literal=False):
        if(not self.check_condition(parent_obj, key)):
            return
        f = parent_obj
        if(len(key) > 0):
            i1 = key[0]
        if(len(key) > 1):
            i2 = key[1]
        if(len(key) > 2):
            i3 = key[2]
        if(len(key) > 3):
            i4 = key[3]
        if (type(self.size_field) == int):
            sz = self.size_field
        else:
            sz = eval(self.size_field)
        if(sz == 0):
            self.value(parent_obj)[key] = b''
            return
        if(DEBUG and self.field_name is not None):
            print("Reading: ", self.field_name, " bytes: ", sz - self.size_offset)
        self.value(parent_obj)[key] = fh.read(sz - self.size_offset)
    def get_print(self, parent_obj,key):
        t = self.get(parent_obj,key)
        if (t is None):
            return "Not used"
        if(len(t) == 0):
            return "Not used"
        return "Data length %s" % len(t)

class StringFieldData(FieldData):
    def get_print(self, parent_obj,key):
        t = self.get(parent_obj,key)
        if(len(t) == 0):
            return "Not used"
        return "%s" % t

class NumFieldData(FieldData):
    def __init__(self, field_name, size_field, ty, loop, options):
        self.pack_func = lambda v : pack(self.format, v)
        self.unpack_func = lambda v: unpack(self.format, v)[0]
        super().__init__(field_name, size_field, ty, loop, options)

    def set(self,parent_obj,key,v):
        v = self.pack_func(v)
        super().set(parent_obj,key,v)

    def value(self, parent_obj):
        if(self.field_name not in parent_obj.value):
            parent_obj.value[self.field_name] = defaultdict(lambda : b'')
        if (DEBUG):
            print(self.field_name)
        val = parent_obj.value[self.field_name][0]
        if len(val) == 0:
            #print(parent_obj.value[self.field_name][0])
            return parent_obj.value[self.field_name]
        elif len(val) == 4:
            if (DEBUG):
                print(self.unpack_func(parent_obj.value[self.field_name][0]))
            return self.unpack_func(parent_obj.value[self.field_name][0])
        else:
            raise RuntimeError("This data type of length %d is not supported" % len(val))

    def get(self,parent_obj,key):
        if(self.loop is not None):
            self.loop.check_index(parent_obj, key)
        if(not self.check_condition(parent_obj, key)):
            return None
        if (DEBUG):
            print(self.value(parent_obj)[key])
        return self.unpack_func(self.value(parent_obj)[key])
    def get_print(self, parent_obj,key):
        t = self.get(parent_obj,key)
        return "%s" % t

class IntFieldData(NumFieldData):
    def __init__(self, field_name, size_field, ty, loop, options):
        self.print_format = '%d'
        self.signed = options.get("signed", False)
        super().__init__(field_name, size_field, ty, loop, options)

    def set_format(self, parent_obj):
        f = parent_obj
        if type(self.size_field) is int:
            sz = self.size_field
        elif type(self.size_field) is str:
            sz = eval(self.size_field)
        else:
            raise Exception("I don't know how to handle this type of size_field")

        if (sz is 1 and self.signed is False):
            self.format = '>B'
        elif (sz is 1 and self.signed is True):
            self.format = '>b'
        elif (sz is 2 and self.signed is False):
            self.format = '>H'
        elif (sz is 2 and self.signed is True):
            self.format = '>h'
        elif (sz is 3):
            self.pack_func = lambda v : int(v).to_bytes(3, "big",
                                                        signed=self.signed)
            self.unpack_func = lambda v : int.from_bytes(v, "big",
                                                         signed=self.signed)
        elif (sz is 4 and self.signed is False):
            self.format = '>I'
        elif (sz is 4 and self.signed is True):
            self.format = '>i'
        elif (sz is 8 and self.signed is False):
            self.format = '>Q'
        elif (sz is 8 and self.signed is True):
            self.format = '>q'
        else:
            raise Exception("Can't determine number format")

    def set(self,parent_obj,key,v):
        self.set_format(parent_obj)
        super().set(parent_obj,key,v)

    def get(self,parent_obj,key):
        self.set_format(parent_obj)
        return super().get(parent_obj,key)

    def get_print(self, parent_obj,key):
        t = self.get(parent_obj,key)
        if(t is None):
            return "Not used"
        return self.print_format % t

class FloatFieldData(NumFieldData):
    def __init__(self, field_name, size_field, ty, loop, options):
        self.format = '>f'
        super().__init__(field_name, size_field, ty, loop, options)

    def get_print(self, parent_obj,key):
        t = self.get(parent_obj,key)
        if(t is None):
            return "Not used"
        return "%f" % t

logger = logging.getLogger('nitf_diff')
class FieldStructDiff(NitfDiffHandle):
    '''Base class for comparing the various NITF Field Structure objects
    (e.g., NitfFileHeader).

    While we could just create new NitfDiffHandle objects for each
    structure (e.g., each of the TREs in the file), we instead try to
    provide a good deal of functionality through "configuration". The
    configuration is a dictionary type object that derived class get
    from the nitf_diff object.  This then contains keyword/value pairs
    for controlling things. While derived classes can others, these
    are things that can be defined:

    exclude           - list of fields to exclude from comparing
    exclude_but_warn  - list of fields to exclude from comparing, but warn if 
                        different
    include           - if nonempty, only include the given fields
    eq_fun            - a dictionary going from field name to a function
                        to compare
    rel_tol           - a dictionary going from field name to a relative
                        tolerance. Only used for fields with float type.
    abs_tol           - a dictionary going from field name to absolute
                        tolerance. Only used for fields with float type.

    If a function isn't otherwise defined in eq_fun, we use operator.eq, 
    except for floating point numbers. For floating point numbers we use
    math.isclose. The rel_tol and/or abs_tol can be supplied. The default
    values are used for math.isclose if not supplied (so 1e-9 and 0.0).
    
    For array/loop fields we compare the shape, and if the same we compare
    each element in the array.
    '''
    def configuration(self, nitf_diff):
        '''Derived class should extract out the appropriate configuration
        from the supplied NitfDiff object.'''
        # Default is no configuration
        return {}
    def _is_diff_ignored(self, s, *args):
        logger.difference_ignored(s, *args)
    def _is_diff(self, s, *args):
        logger.difference(s, *args)
        self.is_same = False

    def handle_diff(self, obj1, obj2, nitf_diff):
        '''Derived class will likely override this to check for their
        specific types'''
        if(not isinstance(obj1, _FieldStruct) or
           not isinstance(obj2, _FieldStruct)):
            return (False, None)
        return (True, self.compare_obj(obj1, obj2, nitf_diff))
    
    def compare_obj(self, obj1, obj2, nitf_diff):
        c = self.configuration(nitf_diff)
        exclude = c.get('exclude', [])
        exclude_but_warn = c.get('exclude_but_warn', [])
        include = c.get('include', [])
        eq_fun = c.get('eq_fun', {})
        rel_tol = c.get('rel_tol', {})
        abs_tol = c.get('abs_tol', {})
        self.is_same = True
        for (fn1, v1), (fn2, v2) in \
            itertools.zip_longest(obj1.items(array_as_list=False),
                                  obj2.items(array_as_list=False),
                                  fillvalue=("No_field", None)):
            if(fn1 != fn2):
                logger.difference("different fields found. Field in object 1 is %s and object 2 is %s. Stopping comparison." % (fn1, fn2))
                return False
            if fn1 in exclude:
                continue
            if len(include) > 0 and fn1 not in include:
                continue
            if fn1 in exclude_but_warn:
                rep_diff = self._is_diff_ignored
            else:
                rep_diff = self._is_diff
            if(isinstance(v1, float) or (isinstance(v1, FieldValueArray) and
                                         v1.type() == float)):
                def _f(a,b):
                    if(a is None and b is None):
                        return True
                    if(a is None or b is None):
                        return False
                    return math.isclose(a,b,rel_tol = rel_tol.get(fn1, 1e-9),
                                        abs_tol = abs_tol.get(fn1, 0.0))
                def_eq_fun = _f
            else:
                def_eq_fun = operator.eq
            cmp_fun = eq_fun.get(fn1, def_eq_fun) 
            if(isinstance(v1, FieldValueArray)):
                if(not FieldValueArray.is_shape_equal(v1, v2)):
                    rep_diff("%s: array shapes are different", fn1)
                    continue
                diff_count = 0
                total_count = 0
                if(v1.shape() is not None):
                    for (ind, av1), av2 in itertools.zip_longest(v1.items(),
                                                                 v2.values()):
                        total_count += 1
                        if(not cmp_fun(av1, av2)):
                            ind_str = ", ".join(str(i) for i in ind)
                            logger.difference_detail("%s[%s]: %s != %s",
                                                     fn1, ind_str, av1, av2)
                            diff_count += 1
                if(diff_count > 0):
                    rep_diff("%s: array had %d of %d different", fn1, 
                             diff_count, total_count)
                continue
            if not cmp_fun(v1, v2):
                rep_diff("%s: %s != %s", fn1, v1, v2)
        return self.is_same

class _create_nitf_field_structure(object):
    # The __dict__ is at class level
    def __init__(self):
        self.d = dict()
        self.d["field_value_list"] = []
        self.d["field_map"] = {}
    def process(self,description):
        desc = copy.deepcopy(description)
        while(len(desc) > 0):
            self.process_row(desc.pop(0), self.d["field_value_list"])
        return self.d
    def process_row(self,row, field_value_list, loop = None):
        # Determine if we have a looping construct, or a simple field.
        if(isinstance(row[0], list)):
            if(loop):
                sz = copy.copy(loop.size)
            else:
                sz = []
            sz.append(row.pop(0)[1])
            lp = _FieldLoopStruct(sz)
            while(len(row) > 0):
                self.process_row(row.pop(0), lp.field_value_list, lp)
            field_value_list.append(lp)
            return
        # If we are here, then this is a simple field
        #field_name, desc, ln, ty, *rest = row
        # Write this so it also works in python 2.7
        field_name, desc, ln, ty, rest = row[0],row[1],row[2],row[3],row[4:]
        options = {}
        if(len(rest) > 0):
            options = rest[0]
        if('field_value_class' in options):
            fv = options["field_value_class"](field_name, ln, ty, loop,
                                              options)
        else:
            fv = _FieldValue(field_name, ln, ty, loop, options)
        if(field_name is not None):
            self.d[field_name] = _FieldValueAccess(fv)
            self.d["field_map"][field_name] = fv
        field_value_list.append(fv)
        
def hardcoded_value(v):
    '''Create a function that returns a fixed value, useful for creating
    various blah_value functions'''
    def f(self, key=None):
        return v
    return f

class NitfLiteral(object):
    '''Sometimes we have a field with a particularly odd format, and it 
    is easier to just return a literal string to return as the TRE field 
    content. If this is passed, we return the exact string passed, plus
    any padding.'''
    def __init__(self, value, trunc_size = None):
        if(trunc_size is None):
            self.value = str(value)
        else:
            self.value = str(value)[0:(trunc_size-1)]

def create_nitf_field_structure(name, description, hlp = None):
    '''Create a nitf field structure and return a class for dealing with this. 
    The name is the class name, and the description should be a list of
    lists describing the field structure. You can optionally supply a help
    string to put in the classes __doc__, this is recommended but not
    required.

    The class provides a set of functions for each field_name that can be 
    used to return the value of that field (if we have read this from a file)
    or to set that field (if we are writing to a file). Some fields may
    have a looping structure, we present these fields as arrays.

    Take a look at the unit tests in nitf_field_test.py for examples of 
    using this. 

    The class returned can be further modified to add functions such as 
    foo_value. The change the field "foo" so it is no longer something that
    can be set, instead the class calculates the value that this should be.

    For the description, we take a field_name, help description, size,
    type 'ty', and a set of optionally parameters.  

    The field_name can be the "None" object if this needs to reserve
    space but isn't actually a field (e.g., see "USE00A" which has
    lots of reserved fields).  The type might be something like 'int',
    'float' or 'str'. We convert the NITF string to and from this
    type.

    The optional parameters are:

    frmt    - A format string or function
    default - The default value to use when writing. If not specified, the
              default is all spaces for a str and 0 for a number type.
    condition - An expression used to determine if the field is included
              or not.
    optional - If true, a field is optional. Note that this is different than
              conditional - with conditional the bytes for the field might
              or might not be present. With optional, they are always present
              but might be all spaces which indicates the value is not there.
              If optional is present, we translate all spaces in the NITF
              file to and from the python "None" object
    optional_char - There are some TREs that use "-----" instead of "    "
              to indicate missing data. No idea why they don't just use ' ',
              but if there is a different char you can supply it.
    field_value_class - Most fields can be handled by our internal _FieldValue
              class. However there are some special cases (e.g., IXSHD used
              for image segment level TREs). If we need to change this,
              we can supply the class to use here. This class should supply
              a field_name, get, set, loop, write_to_file, read_from_file, 
              and get_print function because these are the things we call. 
              Note that we have a generic FieldData class here, which might 
              be sufficient.

    The 'frmt' can be a format string (e.g., "%03d" for a 3 digit integer),
    or it can be a function that takes a value and returns a string - useful
    for more complicated formatting than can be captured with a format string
    (e.g., file date/time in the format CCYYMMDDhhmmss). The default format
    for str type is just "%s" and integer is "%d" - you don't need to specify
    this if you want the default (note that we already handling padding, so
    you don't need to specify something like "%03d" to get 0 filled padding).
    Floats are more complicated. We have as a default the 
    float_to_fixed_width function. This uses fixed point with the precision
    set to fit (so 0.00001, 0.00010, 10.0000, through 1000000). This often
    but not always works, set the NITF documentation for how the floats 
    should be formatted.
    '''
    t = _create_nitf_field_structure()
    res = type(name, (_FieldStruct,), t.process(description))
    if(hlp is not None):
        try:
            # This doesn't work in python 2.7, we can't write to the
            # doc. Rather than try to do something clever, just punt and
            # skip adding help for python 2.7. This works find with python 3
            res.__doc__ = hlp
        except AttributeError:
            pass
    return res

__all__ = ["FieldValueArray", "FieldData", "StringFieldData", "IntFieldData",
           "FloatFieldData", "hardcoded_value", "NitfLiteral",
           "FieldStructDiff",
           "create_nitf_field_structure", "float_to_fixed_width"]
