from .nitf_diff_handle import NitfDiffHandle
from collections import defaultdict, OrderedDict
import itertools
import operator
import weakref
import copy
import math
from struct import pack, unpack
import logging
import io

# Add a bunch of debugging if you are diagnosing a problem
DEBUG = False

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

class NitfLiteral(object):
    '''Sometimes we have a field with a particularly odd format, and it 
    is easier to just return a literal string to return as the TRE field 
    content. If this is passed, we return the exact string passed, plus
    any padding.'''
    def __init__(self, value, trunc_size = None):
        if(trunc_size is None):
            self.value = bytes(value)
        else:
            self.value = bytes(value)[0:(trunc_size-1)]

def _eval_or_exec_expr(fs, key, expr, do_eval):
    '''We have a few places where we evaluate or execute an expression,
    with various local variables set up for the evaluation context. As
    a convenience we centralize this to one place, so there is only
    one function to update if we add new variables (e.g., add to the number
    of index variables).'''
    f = fs
    if(len(key) > 0):
        i1 = key[0]
    if(len(key) > 1):
        i2 = key[1]
    if(len(key) > 2):
        i3 = key[2]
    if(len(key) > 3):
        i4 = key[3]
    if(do_eval):
        return eval(expr)
    else:
        exec(expr)
    
class NitfField(object):
    '''A NITF field is complicated enough that we have a separate class
    to handle it. This class worries about the looping structure, conditional
    and optional fields, etc.'''
    def __init__(self, fs, field_name, size, ty, loop, options):
        '''Give the size, type, loop structure, and options to to use. If
        default is given as None, we use a default default value of
        all spaces for type 'str' or 0 for type int or float.

        The fs should point to the parent FieldStruct, so we can do things
        like check conditions. 
        '''
        # Allow fs to be None, as an aid with unit testing
        if(fs is None):
            self.fs = None
            self.fs_name = "None"
        else:
            self.fs = fs
            self.fs_name = type(fs).__name__
        self.field_name = field_name
        self._size = size
        self.size_offset = options.get("size_offset", 0)
        self.size_not_updated = options.get("size_not_updated", False)
        self.ty = ty
        self.loop = None
        if(loop):
            self.loop = weakref.proxy(loop)
        self.frmt = options.get("frmt", None)
        self.default = options.get("default", None)
        self.condition = options.get("condition", None)
        self.optional = options.get("optional", False)
        self.optional_char = options.get("optional_char", " ")
        self.hardcoded_value = options.get("hardcoded_value", False)
        self.value_func = options.get("value", None)
        # Have a dictionary that maps the index/looping key to a value.
        # To prevent needing special handling, a single value is still
        # treated as a dict with a key of (). You
        # get the value by self.value_dict[key].  
        if(self.field_name is None):
            self.value_dict = None
        if(self.default is not None):
            self.value_dict = defaultdict(lambda : self.default)
        elif(self.optional):
            self.value_dict = defaultdict(lambda : None)
        elif(self.ty == str):
            self.value_dict = defaultdict(lambda : "")
        else:
            self.value_dict = defaultdict(lambda : 0)
        # Second version that saves the raw data. I don't think saving
        # data twice will be a problem, but if it is we can come back
        # to this.
        self.raw_value_dict = {}
        # Location data was written in file, used by update_file.
        self.fh_loc = {}
        # If true, then we check the size of data set by __setitem__.
        # This is really meant for the derived class FieldData where
        # we separately handling going to and from bytes.
        self._check_or_set_size = False

    @property
    def has_loop(self):
        return self.loop.dim_size != 0

    @property
    def dim_size(self):
        '''The dimension size of this field (e.g., 2d, 3d). For a scalar
        this returns 0.'''
        return self.loop.dim_size

    def shape(self, key):
        return self.loop.shape(key)

    @classmethod
    def is_shape_equal(cls, fld1, fld2, lead=()):
        '''Return True if the shape of fld1 and fld2 are the same,
        False otherwise'''
        return NitfLoop.is_shape_equal(fld1.loop, fld2.loop)
    
    def to_list(self):
        '''Return the data as a nested list. Scalar items as returned as a 
        scalar'''
        return self.loop.to_list(self)

    def values(self):
        '''Iterate through values. This uses the 'C' like order, where we
        vary the last index the fastest. This is like doing a flatten on 
        the results of to_list'''
        for k in self.loop.keys():
            yield self[k]
                        
    def items(self):
        '''Likes values(), but iterator through a tuple of the (index,value)
        instead of just values.'''
        for k in self.loop.keys():
            yield (k, self[k])
    
    def size(self, key):
        '''Return the size. In the simplest case, this is just self._size,
        but if self._size is an expression then we evaluate it. We also
        apply size_offset'''
        if (type(self._size) == int):
            sz = self._size
        else:
            sz = self.eval_expr(self.key_as_tuple(key), self._size)
        if(sz != 0):
            sz -= self.size_offset
        return sz

    def _set_size(self, key, sz):
        '''Set the value given by the sz expression'''
        if(sz == 0):
            self.exec_expr(key, "%s = 0" % self._size)
        else:
            self.exec_expr(key, "%s = %d" % (self._size, sz + self.size_offset))

    def _format_val(self, v, sz):
        '''Format a value to a given size.'''
        # The format string fstring is used to add the proper padding to give
        # the full size. For string is padded with spaces on the left. For
        # integers we pad on the right with 0.
        fstring = "{:%ds}" % sz
        frmt = "%s"
        if(self.ty == int):
            fstring = "{:s}"
            frmt = "%%0%dd" % sz
        if(self.ty == float):
            fstring = "{:%ds}" % sz
            frmt = lambda v : float_to_fixed_width(v, sz)
        if(self.frmt):
            frmt = self.frmt
        if(isinstance(frmt, str)):
            t = fstring.format(frmt % v)
        else:
            t = fstring.format(frmt(v))
        return t
        
    def get_print(self, key):
        '''Return string suitable for printing. This is either the 
        value of this field, or "Not used" if the condition isn't met.'''
        t = self[key]
        if(t is None):
            t = "Not used"
        return str(t)

    def eval_expr(self, key, expr):
        '''This is used to evaluate an expression. In this expression,
        'f' if the FieldStruct, i1 through i4 are indices. So this
        might be 'f.foo[i1,i2]' '''
        return _eval_or_exec_expr(self.fs, key, expr, True)

    def exec_expr(self, key, expr):
        '''This is used to execute an expression. In this expression,
        'f' if the FieldStruct, i1 through i4 are indices. So this
        might be 'f.foo[i1,i2]' '''
        _eval_or_exec_expr(self.fs, key, expr, False)
    
    def check_condition(self, key):
        '''Evaluate the condition (if present) and return False if it isn't
        met, True if it is or if there is no condition'''
        if(self.condition is None):
            return True
        v = self.eval_expr(key, self.condition)
        if(DEBUG):
            print("Condition: " + self.condition)
            print("eval: " + str(v))
        return v

    def key_as_tuple(self, key):
        '''Handle degenerate case of single value, making it a tuple so
        we don't need any special handling in other code.'''
        if(not isinstance(key, tuple)):
            return (key,)
        return key
    
    def get_raw_bytes(self, key):
        '''Like self[key], but returns the raw bytes in the NITF file 
        without converting to the field type.'''
        k = self.key_as_tuple(key)
        if(k in self.raw_value_dict):
            return self.raw_value_dict[k].value
        return self.bytes(k)
    
    def __getitem__(self, key):
        if(self.field_name is None):
            return ''
        k = self.key_as_tuple(key)
        if(self.loop is not None):
            self.loop.check_index(k)
        if(not self.check_condition(k)):
            return None
        try:
            v = None
            if(self.value_func is not None):
                v = self.value_func(self.fs, k)
            else:
                v = self.value_dict[k]
            if(self.optional and v is None):
                return None
            if(isinstance(v, NitfLiteral)):
                v = v.value
                if(self.optional and
                   v.rstrip(self.optional_char.encode('utf-8') + b' ') == b''):
                    return None
            if(self.ty == str):
                if(isinstance(v, bytes)):
                    return v.decode("utf-8").rstrip()
                return self.ty(v).rstrip()
            else:
                return self.ty(v)
        except Exception as e:
            if(self.loop is None):
                raise RuntimeError("Error occurred getting '%s' from '%s'. Value '%s'" % (self.field_name, self.fs_name, v)) from e
            else:
                raise RuntimeError("Error occurred getting '%s[%s]' from '%s'. Value '%s'" % (self.field_name, key, self.fs_name, v)) from e
            
    def __setitem__(self, key, v):
        if(self.field_name is None):
            raise RuntimeError("Can't set a reserved field")
        k = self.key_as_tuple(key)
        if(self.loop is not None):
            self.loop.check_index(k)
        if(not self.check_condition(k)):
            raise RuntimeError("Can't set value for field %s because the condition '%s' isn't met" % (self.field_name, self.condition))
        if(self.hardcoded_value or self.value_func):
            raise RuntimeError("Can't set value for field " + self.field_name)
        # If we are implementing the TRE in its own object, don't allow
        # the raw values to be set
        if(self.fs and hasattr(self.fs, "tre_implementation_field") and
           self.fs.tre_implementation_field is not None):
            raise RuntimeError("You can't directly set fields in %s TRE. Instead, set this through the %s object" % (self.fs.cetag_value(), self.fs.tre_implementation_field))
        if(v is None and not self.optional):
            raise RuntimeError("Can only set a field to 'None' if it is marked as being optional")
        self.value_dict[k] = v
        if k in self.raw_value_dict:
            del self.raw_value_dict[k]
        if self._check_or_set_size:
            if(self.size_not_updated):
                sz = self.size(k)
                if(len(v) != sz):
                    raise RuntimeError("FieldData was expected to be exactly %d bytes, but data that we tried to set was instead %d bytes" % (sz, len(v)))
            else:
                self._set_size(k, len(v))
 
    def bytes(self, key=()):
        '''Return bytes version of this value, formatted and padded as
        NITF will store this.'''
        # If we have a NitfLiteral we assume some sort of funky formating
        # that is handled outside of this class. Pad, but otherwise don't
        # process this.
        k = self.key_as_tuple(key)
        sz = self.size(k)
        if(isinstance(self.value_dict[k], NitfLiteral)):
            t = self.value_dict[k].value.ljust(sz)
        else:
            # Otherwise, get the value and do the formatting that has been
            # supplied to us. Note that we have the explicit getitem in call
            # here because FieldData may override this, but we want this low
            # level raw value
            v = NitfField.__getitem__(self,k)
            if(v is None and self.optional):
                t = ("{:%ds}" % sz).format("").replace(" ", self.optional_char)
            elif self.ty == bytes:
                t = v
            else:
                t = self._format_val(v, sz)
        if(len(t) != sz):
            raise RuntimeError("Formatting error. String '%s' is not right length for NITF field %s" % (t, self.field_name))
        if(self.ty == bytes or isinstance(self.value_dict[k], NitfLiteral)):
            return t
        else:
            return t.encode("utf-8")
        
    def write_to_file(self, fh, key):
        k = self.key_as_tuple(key)
        if(not self.check_condition(k)):
            return
        if(self.field_name is not None):
            if(DEBUG):
                print("Writing: ", self.field_name, self.bytes(k))
            self.fh_loc[k] = fh.tell()
        fh.write(self.bytes(k))
        
    def update_file(self, fh, key):
        '''Rewrite to a file after the value of this field has been updated'''
        # Not sure if updating a field that doesn't meet the condition should
        # just be a noop, or an error. For now treat as an error but we can
        # change this behavior if needed.
        k = self.key_as_tuple(key)
        if(not self.check_condition(k)):
            raise RuntimeError("Can't update value for field %s because the condition '%s' isn't met" % (self.field_name, self.condition))
        if(DEBUG):
            print("Updating: ", self.field_name)
        last_pos = fh.tell()
        fh.seek(self.fh_loc[k])
        fh.write(self.bytes(k))
        fh.seek(last_pos)
        
    def read_from_file(self, fh, nitf_literal, key):
        k = self.key_as_tuple(key)
        if(not self.check_condition(k)):
            return
        sz = self.size(k)
        if(DEBUG and self.field_name is not None):
            print("Reading: ", self.field_name, " bytes: ", sz)
        t = fh.read(sz)
        if(DEBUG and self.field_name is not None):
            print("Value: " + str(t))
        if(len(t) != sz):
            raise RuntimeError("Not enough bytes left to read %d bytes for field %s" % (sz, self.field_name))
        if(self.field_name is not None):
            try:
                self.raw_value_dict[k] = NitfLiteral(t)
                if(nitf_literal):
                    self.value_dict[k] = NitfLiteral(t)
                elif(self.optional and
                 t.rstrip(self.optional_char.encode('utf-8') + b' ') == b''):
                    self.value_dict[k] = None
                elif(self.ty == str):
                    self.value_dict[k] = t.rstrip().decode("utf-8", "replace")
                elif(self.ty == bytes):
                    # Don't strip spaces or nulls, since these are valid
                    # byte values
                    self.value_dict[k] = self.ty(t)
                else:
                    v = t.rstrip()
                    if(v == b''):
                        raise RuntimeError("Empty string read for field %s" % self.field_name)
                    self.value_dict[k] = self.ty(v)
            except Exception as e:
                raise Exception("Exception while parsing ", self.field_name, " from ", t.rstrip(), "underlying error: ", e)

class FieldData(NitfField):
    '''Class to handle generic variable size data, which in some cases
    might be binary data.
    
    Derived classes should supply a "pack" and "unpack" function to take
    the underlying data to and from bytes.  Often derived classes will
    also want to supply a different get_print function.
    '''
    def __init__(self, fs, field_name, size, ty, loop, options):
        super().__init__(fs, field_name, size, bytes, loop, options)
        self._check_or_set_size = True
        
    def pack(self, key, val):
        '''Return bytes representing the given value.'''
        raise NotImplementedError()

    def unpack(self, key, bdata):
        '''Unpack the bytes bdate and return value.'''
        raise NotImplementedError()

    def __getitem__(self, key):
        t = super().__getitem__(key)
        if(t is not None):
            return self.unpack(key, t)
        return None
    
    def __setitem__(self, key, v):
        if(v is not None):
            super().__setitem__(key, self.pack(key, v))
        else:
            super().__setitem__(key, self.pack(key, None))
            
class StringFieldData(FieldData):
    def get_print(self, key):
        t = self[key]
        if(t is None or len(t) == 0):
            return "Not used"
        return "%s" % t

    def unpack(self, key, bdata):
        return bdata.decode("utf-8")

    def pack(self, key, v):
        if(isinstance(v, bytes)):
            return v
        return v.encode("utf-8")

class BytesFieldData(FieldData):
    def get_print(self, key):
        t = self[key]
        if(t is None or len(t) == 0):
            return "Not used"
        return "Data length %s" % len(t)

    def unpack(self, key, bdata):
        return bdata

    def pack(self, key, v):
        if(isinstance(v, bytes)):
            return v
        return v.encode("utf-8")
    
class FloatFieldData(FieldData):
    def get_print(self, key):
        t = self[key]
        if(t is None):
            return "Not used"
        return "%f" % t

    def unpack(self, key, bdata):
        return unpack(">f", bdata)[0]

    def pack(self, key, v):
        return pack(">f", v)

class IntFieldData(FieldData):
    def __init__(self, fs, field_name, size, ty, loop, options):
        super().__init__(fs, field_name, size, ty, loop, options)
        self.signed = options.get("signed", False)
        
    def get_print(self, key):
        t = self[key]
        if(t is None):
            return "Not used"
        return "%d" % t

    def unpack(self, key, bdata):
        sz = self.size(key)
        if (sz is 1 and self.signed is False):
            return unpack(">B", bdata)[0]
        elif (sz is 1 and self.signed is True):
            return unpack(">b", bdata)[0]
        elif (sz is 2 and self.signed is False):
            return unpack(">H", bdata)[0]
        elif (sz is 2 and self.signed is True):
            return unpack(">h", bdata)[0]
        elif (sz is 3):
            return int.from_bytes(bdata, "big", signed=self.signed)
        elif (sz is 4 and self.signed is False):
            return unpack(">I", bdata)[0]
        elif (sz is 4 and self.signed is True):
            return unpack(">i", bdata)[0]
        elif (sz is 8 and self.signed is False):
            return unpack(">Q", bdata)[0]
        elif (sz is 8 and self.signed is True):
            return unpack(">q", bdata)[0]
        else:
            raise Exception("Can't determine number format")
        
    def pack(self, key, v):
        sz = self.size(key)
        if (sz is 1 and self.signed is False):
            return pack(">B", v)
        elif (sz is 1 and self.signed is True):
            return pack(">b", v)
        elif (sz is 2 and self.signed is False):
            return pack(">H", v)
        elif (sz is 2 and self.signed is True):
            return pack(">h", v)
        elif (sz is 3):
            return int(v).to_bytes(3, "big", signed=self.signed)
        elif (sz is 4 and self.signed is False):
            return pack(">I", v)
        elif (sz is 4 and self.signed is True):
            return pack(">i", v)
        elif (sz is 8 and self.signed is False):
            return pack(">Q", v)
        elif (sz is 8 and self.signed is True):
            return pack(">q", v)
        else:
            raise Exception("Can't determine number format")

class NitfLoop(object):
    '''This handles a NITF looping structure.

    Because it is convenient, we have a "null" pseudo loop as the
    outer loop.  This just allows us to treat the outer fields not in
    a loop the same way we treat the loops.  This is indicated by
    having parent_list None.

    The keys of the pseudo loop are just the list [(),]
    ''' 
    def __init__(self, fs, parent_loop, desc, field):
        '''Note, this also fills in data in the OrderedDict field.'''
        self.fs = fs
        self.parent_list = None
        if(parent_loop):
            if(parent_loop.parent_list):
                self.parent_list = (*parent_loop.parent_list,
                                    weakref.proxy(parent_loop),)
            else:
                self.parent_list = (weakref.proxy(parent_loop),)
        self.field_list = []
        if(self.parent_list):
            if(desc[0][0] != "loop"):
                raise RuntimeError("Error parsing looping structure:\n" + desc)
            self._shape = desc[0][1]
            desc_rest = desc[1:]
        else:
            self._shape = None
            desc_rest = desc
        for row in desc_rest:
            if(isinstance(row[0], list)):
                self.field_list.append(NitfLoop(self.fs, self, row, field))
            else:
                field_name, desc, size, ty, rest = row[0],row[1],row[2],row[3],row[4:]
                options = {}
                if(len(rest) > 0):
                    options = rest[0]
                fv = options.get("field_value_class", NitfField)(self.fs,
                              field_name, size, ty, self, options)
                if(field_name):
                    field[field_name] = fv
                self.field_list.append(fv)
                
    def shape(self, key):
        '''Return size of this dimension.'''
        if(len(key) >= self.dim_size - 1):
            t = _eval_or_exec_expr(self.fs, key, self._shape, True)
            if(t is None):
                t = 0
            return t
        else:
            return self.parent_list[len(key)+1].shape(key)

    @property
    def dim_size(self):
        '''Return the dim size of this loop (e.g., 2d, 3d, etc)'''
        if(self.parent_list is None):
            return 0
        return len(self.parent_list)
    
    def check_index(self, key):
        '''Check if key is within the range of the loops'''
        # Skip if we are null outer loop
        if(self.parent_list is None):
            return
        if(len(key) != self.dim_size):
            raise IndexError()
        if(isinstance(key[-1], slice)):
            raise RuntimeError("FieldStruct doesn't support slices in arrays")
        if(key[-1] < 0 or key[-1] >= self.shape(key[:-1])):
            raise IndexError()

    def key_subloop(self, lead):
        '''Iterate through the set of keys for this specific loop.'''
        if(self.dim_size == 0):
            yield ()
            return
        for i in range(self.shape(lead)):
            yield (*lead,i)
        
    def keys(self,lead=()):
        '''Iterate through all the key tuples.'''
        for k2 in self.key_subloop(lead):
            if(len(k2) == self.dim_size):
                yield k2
            else:
                for j in self.keys(k2):
                    yield j
                    
    def key_to_str(self, key):
        '''Write out key as a string (with handling for key = ())'''
        if(len(key) == 0):
            return ""
        return "[" + ", ".join(str(i) for i in key) + "]"
        
    def write_to_file(self, fh, lead=()):
        '''Write data stored in the loop to a file'''
        for k in self.key_subloop(lead):
            for fv in self.field_list:
                fv.write_to_file(fh, k)
            
    def read_from_file(self, fh, nitf_literal=False, lead=()):
        '''Read data from a file for the fields in this loop'''
        for k in self.key_subloop(lead):
            for fv in self.field_list:
                fv.read_from_file(fh, nitf_literal, k)

    def to_list(self, fld,lead=()):
        '''Return the data in NitfField fld as a nested list. Scalar items 
        are returned as a scalar'''
        if(self.dim_size == 0):
            return fld[()]
        if(len(lead) == self.dim_size - 1):
            return [fld[(*lead, i)] for i in range(self.shape(lead))]
        return [self.to_list(fld, lead=(*lead, i))
                for i in range(self.shape(lead))]

    @classmethod
    def is_shape_equal(cls, loop1, loop2, lead=()):
        '''Check if two loops have the same shape.'''
        if(loop1.dim_size != loop2.dim_size):
            return False
        if(len(lead) == loop1.dim_size - 1):
            return loop1.shape(lead) == loop2.shape(lead)
        for k in loop1.key_subloop(lead):
            if not cls.is_shape_equal(loop1, loop2, lead=k):
                return False
        return True

    def print_to_fh(self, fh):
        '''Print a description of fields in this loop'''
        max_len = max((len(fld.field_name) for fld in self.field_list
                       if(not isinstance(fld, NitfLoop)) and
                       fld.field_name is not None),default=10)
        max_len += max((len(self.key_to_str(k)) for k in self.keys()),
                       default=0)
        if(self.dim_size > 0):
            print("  " * (self.dim_size-1) + "Loop - %s" % self._shape,
                  file=fh)
        lead_space = "  " * self.dim_size
        for f in self.field_list:
            if(isinstance(f, NitfLoop)):
                f.print_to_fh(fh)
            elif(f.field_name is not None):
                for k in self.keys():
                    print(lead_space +
                          (f.field_name + self.key_to_str(k)).ljust(max_len) +
                          ": " + f.get_print(k), file=fh)
                
class FieldStruct(object):
    '''This class is used to handle NITF field structure (e.g., 
    a TRE or NitfFileHeader).

    Note that you are *not* required to use this base class to have a
    class that handles a field structure, but often it is useful to do
    so.

    This takes a "description" which is any array of field rows. For each
    row, we take a field_name, help description, size, type 'ty', and
    a set of optionally parameters. Rows can be nested with a "loop"
    structure. So a sample field structure description might be:

        [["fhdr", "", 4, str, {"default" : "NITF"}],
         ["numi", "", 3, int],
         [["loop", "f.numi"],
          ['lish', "", 6, int],
          ['li', "", 10, int]]
        ]

    The size can be an expression, e.g. "f.foo[i1,i2]". See 
    NitfField.eval_expr.

    The field_name can be the "None" object if this needs to reserve
    space but isn't actually a field (e.g., see "USE00A" which has
    lots of reserved fields).  The type might be something like 'int',
    'float' or 'str'. We convert the NITF string to and from this
    type.

    The optional parameters are:

    frmt    - A format string or function
    default - The default value to use when writing. If not specified, the
              default is all spaces for a str and 0 for a number type.
    hardcoded_value - If True, do not allow the value to be modified. It
              is set to the default value, and trying to change it gives
              an error.
    value   - Some fields aren't really independent, but rather are calculated
              from other fields. If supplied, this gives a function that
              should take the FieldStruct and Key, and return a value.
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
    field_value_class - Most fields can be handled by NitfField
              class. However there are some special cases (e.g., IXSHD used
              for image segment level TREs). If we need to change this,
              we can supply the class to use here. This class should derive
              from FieldData (or supply the same interface).
    size_offset - In some cases, the 'size' is really the size of the
              data plus something else. For example, in the image 
              header the size of the TRE includes both the TRE and an 
              additional field indicating if we have overflow. You can 
              supply 'size_offset' option to specify an offset that 
              should be applied to the size. The offset is subtracted from
              'size' to give the actual size of this field.
    size_not_updated - See below
    signed  - Used by IntFieldData to determine if data is signed or
              unsigned. Default is False, or unsigned.

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
    but not always works, see the NITF documentation for how the floats 
    should be formatted for a particular field.

    If size is a string to be evaluated, there are two kinds of behavior
    we might want when we set a value:

    1. We want to take the size of the value, and use that to fill in 
       the size expression (e.g., if size is "f.foo[i1, i2]" then update 
       that value). This is useful for example for putting TREs in a
       image header, we don't know what the size is ahead of time and just 
       want to set this.
    2. We know the size, want to hold this fixed, and trigger an error if
       we try to set a value other than this size. This is useful for
       things that are represented as binary data in a TRE, but where the
       size is know ahead of time (e.g., TreENGRDA).

    If size is instead a value (e.g., 10), then we ignore size_not_updated.
    The default is size_not_updated = False. In all cases, this only
    applies if we have a field_value_class.

    For fields that loop, you can access them like an array, e.g. 
    fs.foo[0,1], and assign like fs.foo[0,1] = 2.  Note however that
    we do *not* support slices. This is because in general a NITF loop
    isn't the same size, and might be missing for some indices (e.g.,
    a conditional isn't met). It isn't really clear what a slice means
    when some of the data might not be there, or when different indices
    have different dimensions.
    '''
    def __init__(self, description = None):
        '''If description is not passed in, we use self.desc. This is
        to make it easier for subclasses, you can just define the class
        variable Class.desc to the description to populate this, no need
        to write a __init__ function.'''

        # We have two closely related variables. self.field maps from
        # field name to NitfField, it is focused on accessing the data.
        # self.pseudo_outer_loop is a pseudo outer loop of size 1 for the entire
        # structure including reserve fields (without a field name) and
        # looping structure. It is focused on the layout of the data
        # in the NITF file.
        
        self.pseudo_outer_loop = None
        
        # Note that as of python 3.7 the normal dict preserved insert
        # order. However, we don't want to assume we are using that new
        # of a version. So for now, we use a OrderedDict.
        
        self.field = OrderedDict()
        self._desc_init_none = True
        if(description is not None):
            self.desc = copy.deepcopy(description)
            self._desc_init_none = False
        # Note this also fills in self.field
        self.pseudo_outer_loop = NitfLoop(weakref.proxy(self), None, self.desc,
                                          self.field)

    def __deepcopy__(self, dict):
        '''Generate a deepcopy. 

        This implementation isn't particularly efficient, if we end
        up doing this a lot we can try to do something more intelligent'''
        if(self._desc_init_none):
            res = self.__class__()
        else:
            res = self.__class__(self.desc)
        fh = io.BytesIO()
        self.write_to_file(fh)
        fh2 = io.BytesIO(fh.getvalue())
        res.read_from_file(fh2)
        return res
        
            
    def __getattr__(self, nm):
        if("field" not in self.__dict__):
            raise AttributeError()
        fld = self.__dict__["field"]
        if(nm not in fld):
            raise AttributeError()
        t = fld[nm]
        return t if t.has_loop else t[()]

    def get_raw_bytes(self, nm, key=()):
        '''Return the raw bytes for a field.'''
        fld = self.__dict__["field"]
        if(nm not in fld):
            raise AttributeError()
        return fld[nm].get_raw_bytes(key)
    
    def __setattr__(self, nm, value):
        if("field" in self.__dict__ and nm in self.__dict__["field"]):
            t = self.field[nm]
            if(t.has_loop):
                raise RuntimeError("Need to supply index to %s" % nm)
            t[()] = value
        else:
            super().__setattr__(nm, value)

    def field_names(self):
        '''Return an iterator that returns the field names'''
        for f in self.field.values():
            if(f.field_name is not None):
                yield f.field_name

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
        for f in self.field.values():
            if(f.field_name is not None):
                if(array_as_list):
                    yield (f.field_name, f.to_list())
                else:
                    yield (f.field_name, getattr(self, f.field_name))
                
    def write_to_file(self, fh):
        '''Write to a file stream.'''
        self.pseudo_outer_loop.write_to_file(fh)

    def read_from_file(self, fh, nitf_literal=False):
        '''
        Read from a file stream.

        nitf_literal set to True is to handle odd formatting rules,
        where we want to read the values from a file as a string and
        not apply any additional formatting. The data is read as
        NitfLiteral objects. Normally you don't want this option, but
        it can be useful for cases hard to capture otherwise (e.g.,
        heritage systems that depend on specific formatting).
        '''
        self.pseudo_outer_loop.read_from_file(fh, nitf_literal)
            
    def update_field(self, fh, field_name, value, key = ()):
        '''Update a field name in an open file'''
        fv = self.field[field_name]
        fv[key] = value
        fv.update_file(fh, key)
        
    def __str__(self):
        '''Text description of structure, e.g., something you can print
        out.'''
        res = io.StringIO()
        self.pseudo_outer_loop.print_to_fh(res)
        return res.getvalue()

    def summary(self):
        return "FieldStruct with %d fields" % len(self.field)
                

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
        if(not isinstance(obj1, FieldStruct) or
           not isinstance(obj2, FieldStruct)):
            return (False, None)
        return (True, self.compare_obj(obj1, obj2, nitf_diff))

    def _cmp_func(self, fn1, v1, c):
        '''Compare function to use'''
        rel_tol = c.get('rel_tol', {})
        abs_tol = c.get('abs_tol', {})
        eq_fun = c.get('eq_fun', {})
        if(isinstance(v1, float) or (isinstance(v1, NitfField) and
                                     v1.ty == float)):
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
        return eq_fun.get(fn1, def_eq_fun)

    def _cmp_nitf_field(self, fn1, v1, v2, cmp_func, rep_diff):
        '''Compare a field, which is like an array'''
        if(not NitfField.is_shape_equal(v1, v2)):
            rep_diff("%s: array shapes are different", fn1)
            return
        diff_count = 0
        total_count = 0
        for (ind, av1), av2 in itertools.zip_longest(v1.items(), v2.values()):
            total_count += 1
            if(not cmp_func(av1, av2)):
                ind_str = ", ".join(str(i) for i in ind)
                logger.difference_detail("%s[%s]: %s != %s", fn1, ind_str,
                                         av1, av2)
                diff_count += 1
        if(diff_count > 0):
            rep_diff("%s: array had %d of %d different", fn1, diff_count,
                     total_count)
        
    def compare_obj(self, obj1, obj2, nitf_diff):
        c = self.configuration(nitf_diff)
        exclude = c.get('exclude', [])
        exclude_but_warn = c.get('exclude_but_warn', [])
        include = c.get('include', [])
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
            cmp_func = self._cmp_func(fn1, v1, c)
            if(isinstance(v1, NitfField)):
                self._cmp_nitf_field(fn1, v1, v2, cmp_func, rep_diff)
            elif not cmp_func(v1, v2):
                rep_diff("%s: %s != %s", fn1, v1, v2)
        return self.is_same

    
__all__ = ["FieldStruct", "NitfField", "FieldData", "BytesFieldData",
           "StringFieldData", "FloatFieldData", "IntFieldData",
           "FieldStructDiff", "float_to_fixed_width", "NitfLiteral"]
