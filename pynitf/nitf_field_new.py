from .nitf_field import float_to_fixed_width, NitfLiteral
from collections import defaultdict
import weakref
import copy
from struct import pack, unpack

# Add a bunch of debugging if you are diagnosing a problem
DEBUG = False

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
            self.fs = weakref.proxy(fs)
            self.fs_name = type(fs).__name__
        self.field_name = field_name
        self._size = size
        self.size_offset = options.get("size_offset", 0)
        self.size_not_updated = options.get("size_not_updated", False)
        self.ty = ty
        self.loop = loop
        self.frmt = options.get("frmt", None)
        self.default = options.get("default", None)
        self.condition = options.get("condition", None)
        self.optional = options.get("optional", False)
        self.optional_char = options.get("optional_char", " ")
        self.hardcoded_value = options.get("hardcoded_value", False)
        # Have s a dictionary that maps the index/looping key to a value.
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
        # Location data was written in file, used by update_file.
        self.fh_loc = {}
        # If true, then we check the size of data set by __setitem__.
        # This is really meant for the derived class FieldData where
        # we separately handling going to and from bytes.
        self._check_or_set_size = False

    def size(self, key):
        '''Return the size. In the simplest case, this is just self._size,
        but if self._size is an expression then we evaluate it. We also
        apply size_offset'''
        if (type(self._size) == int):
            sz = self._size
        else:
            sz = self.eval_expr(key, self._size)
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
        f = self.fs
        if(len(key) > 0):
            i1 = key[0]
        if(len(key) > 1):
            i2 = key[1]
        if(len(key) > 2):
            i3 = key[2]
        if(len(key) > 3):
            i4 = key[3]
        return eval(expr)

    def exec_expr(self, key, expr):
        '''This is used to execute an expression. In this expression,
        'f' if the FieldStruct, i1 through i4 are indices. So this
        might be 'f.foo[i1,i2]' '''
        f = self.fs
        if(len(key) > 0):
            i1 = key[0]
        if(len(key) > 1):
            i2 = key[1]
        if(len(key) > 2):
            i3 = key[2]
        if(len(key) > 3):
            i4 = key[3]
        print("Executing: %s" % expr)
        exec(expr)
    
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
    
    def get_raw_bytes(self, key):
        '''Like self[key], but returns the raw bytes in the NITF file 
        without converting to the field type.'''
        t = self.value_dict[key]
        if(not isinstance(t, NitfLiteral)):
            raise RuntimeError("get_no_type_conversion can only be called if data is a NitfLiteral (e.g. read was done with nitf_literal=True)")
        return t.value
    
    def __getitem__(self, key):
        if(self.field_name is None):
            return ''
        if(self.loop is not None):
            self.loop.check_index(key)
        if(not self.check_condition(key)):
            return None
        try:
            v = None
            v = self.value_dict[key]
            if(self.optional and v is None):
                return None
            if(isinstance(v, NitfLiteral)):
                v = v.value
                if(self.optional and
                   v.rstrip(self.optional_char.encode('utf-8') + b' ') == b''):
                    return None
            if(self.ty == str):
                return self.ty(v).rstrip()
            else:
                return self.ty(v)
        except Exception as e:
            if(self.loop is None):
                raise RuntimeError("Error occurred getting '%s' from '%s'. Value '%s'" % (self.field_name, self.fs_name, v)) from e
            else:
                raise RuntimeError("Error occurred getting '%s[%s]' from '%s'. Value '%s'" % (self.field_name, key, self.fs_name, v)) from e
            
    def __setitem__(self,key,v):
        if(self.field_name is None):
            raise RuntimeError("Can't set a reserved field")
        if(self.loop is not None):
            self.loop.check_index(key)
        if(not self.check_condition(key)):
            raise RuntimeError("Can't set value for field %s because the condition '%s' isn't met" % (self.field_name, self.condition))
        if(self.hardcoded_value):
            raise RuntimeError("Can't set value for field " + self.field_name)
        # If we are implementing the TRE in its own object, don't allow
        # the raw values to be set
        if(self.fs and hasattr(self.fs, "tre_implementation_field")):
            raise RuntimeError("You can't directly set fields in %s TRE. Instead, set this through the %s object" % (self.fs.cetag_value(), self.fs.tre_implementation_field))
        if(v is None and not self.optional):
            raise RuntimeError("Can only set a field to 'None' if it is marked as being optional")
        self.value_dict[key] = v
        if self._check_or_set_size:
            if(self.size_not_updated):
                sz = self.size(key)
                if(len(v) != sz):
                    raise RuntimeError("FieldData was expected to be exactly %d bytes, but data that we tried to set was instead %d bytes" % (sz, len(v)))
            else:
                self._set_size(key, len(v))
        
    def bytes(self, key=()):
        '''Return bytes version of this value, formatted and padded as
        NITF will store this.'''
        # If we have a NitfLiteral we assume some sort of funky formating
        # that is handled outside of this class. Pad, but otherwise don't
        # process this.
        sz = self.size(key)
        if(isinstance(self.value_dict[key], NitfLiteral)):
            t = ("{:%ds}" % sz).format(self.value_dict[key].value)
        else:
            # Otherwise, get the value and do the formatting that has been
            # supplied to us. Note that we have the explicit getitem to call
            # here because FieldData may override this, but we want this low
            # level raw value
            v = NitfField.__getitem__(self,key)
            if(v is None and self.optional):
                t = ("{:%ds}" % sz).format("").replace(" ", self.optional_char)
            elif self.ty == bytes:
                t = v
            else:
                t = self._format_val(v, sz)
        if(len(t) != sz):
            raise RuntimeError("Formatting error. String '%s' is not right length for NITF field %s" % (t, self.field_name))
        if(self.ty == bytes):
            return t
        else:
            return t.encode("utf-8")
        
    def write_to_file(self, key, fh):
        if(not self.check_condition(key)):
            return
        if(self.field_name is not None):
            if(DEBUG):
                print("Writing: ", self.field_name, self.bytes(key))
            self.fh_loc[key] = fh.tell()
        fh.write(self.bytes(key))
        
    def update_file(self, key, fh):
        '''Rewrite to a file after the value of this field has been updated'''
        # Not sure if updating a field that doesn't meet the condition should
        # just be a noop, or an error. For now treat as an error but we can
        # change this behavior if needed.
        if(not self.check_condition(key)):
            raise RuntimeError("Can't update value for field %s because the condition '%s' isn't met" % (self.field_name, self.condition))
        if(DEBUG):
            print("Updating: ", self.field_name)
        last_pos = fh.tell()
        fh.seek(self.fh_loc[key])
        fh.write(self.bytes(key))
        fh.seek(last_pos)
        
    def read_from_file(self, key, fh, nitf_literal=False):
        if(not self.check_condition(key)):
            return
        sz = self.size(key)
        if(DEBUG and self.field_name is not None):
            print("Reading: ", self.field_name, " bytes: ", sz)
        t = fh.read(sz)
        if(DEBUG and self.field_name is not None):
            print("Value: " + str(t))
        if(len(t) != sz):
            raise RuntimeError("Not enough bytes left to read %d bytes for field %s" % (sz, self.field_name))
        if(self.field_name is not None):
            try:
                if(nitf_literal):
                    self.value_dict[key] = NitfLiteral(t)
                elif(self.optional and
                 t.rstrip(self.optional_char.encode('utf-8') + b' ') == b''):
                    self.value_dict[key] = None
                elif(self.ty == str):
                    self.value_dict[key] = t.rstrip().decode("utf-8", "replace")
                elif(self.ty == bytes):
                    # Don't strip spaces or nulls, since these are valid
                    # byte values
                    self.value_dict[key] = self.ty(t)
                else:
                    v = t.rstrip()
                    if(v == b''):
                        raise RuntimeError("Empty string read for field %s" % self.field_name)
                    self.value_dict[key] = self.ty(v)
            except Exception as e:
                raise Exception("Exception while parsing ", self.field_name, " from ", t.rstrip(), "underlying error: ", e)

class FieldDataNew(NitfField):
    '''Class to handle generic variable size data.  
    
    Derived classes should supply a "pack" and "unpack" function to take
    the underlying data to and from bytes.  Often derived classes will
    also want to supply different get_print function also'''
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
        return self.unpack(key, super().__getitem__(key))
    
    def __setitem__(self, key, v):
        super().__setitem__(key, self.pack(key, v))

class StringFieldDataNew(FieldDataNew):
    def get_print(self, key):
        t = self[key]
        if(len(t) == 0):
            return "Not used"
        return "%s" % t

    def unpack(self, key, bdata):
        return bdata.decode("utf-8")

    def pack(self, key, v):
        if(isinstance(v, bytes)):
            return v
        return v.encode("utf-8")

class FloatFieldDataNew(FieldDataNew):
    def get_print(self, key):
        t = self[key]
        if(len(t) == 0):
            return "Not used"
        return "%f" % t

    def unpack(self, key, bdata):
        return unpack(">f", bdata)[0]

    def pack(self, key, v):
        return pack(">f", v)

class IntFieldDataNew(FieldDataNew):
    def __init__(self, fs, field_name, size, ty, loop, options):
        super().__init__(fs, field_name, size, ty, loop, options)
        self.signed = options.get("signed", False)
        
    def get_print(self, key):
        t = self[key]
        if(len(t) == 0):
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
    
class FieldStructNew(object):
    '''This class is used to handle NITF field structure (e.g., 
    a TRE or NitfFileHeader).

    Note that you are *not* required to use this base class to have a
    class that handles a field structure, but often it is useful to do
    so.

    This takes a "description" which is any array of fields. For each
    row, we take a field_name, help description, size, type 'ty', and
    a set of optionally parameters.

    size can be an expression, e.g. "f.foo[i1,i2]". See 
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
    '''
    def __init__(self, description):
        self.desc = copy.deepcopy(description)
        self.field_name = [d[0] for d in self.desc if d[0]]
        self.value = {}
        self.default_value = {}
        #for d in self.desc if d[0]:
            
    def __getattr__(self, nm):
        if(nm not in self.field_name):
            raise AttributeError()
        return self.value.get(nm, self.default_value[nm])
    def __setattr__(self, nm, value):
        raise AttributeError()
        
__all__ = ["FieldStructNew", "NitfField", "FieldDataNew",
           "StringFieldDataNew", "FloatFieldDataNew", "IntFieldDataNew"]
