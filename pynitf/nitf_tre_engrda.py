from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six
from collections import MutableMapping
import numpy as np

hlp = '''This is the ENGRDA TRE, Engineering data.

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (STDI-0002 V4.0, available at
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for
where in the document a particular TRE is defined.

ENGRDA is documented at N-9.

We add a dict like interface to ENGRDA. This can be used to read or write
engineering data. See the nitf_tre_engrda_test.py for examples of this.
'''
desc = ["ENGRDA",
        ["resrc", "Unique Source System Name", 20, str],
        ["recnt", "Record entry count", 3, int],
        [["loop", "f.recnt"],
         ["engln", "Engineering Data Label Length", 2, int],
         ["englbl", "Engineering Data Label", "f.engln[i1]", None,
          {'field_value_class' : StringFieldData}],
         ["engmtxc", "Engineering Matrix Data Column Count", 4, int],
         ["engmtxr", "Engineering Matrix Data Row Count", 4, int],
         ["engtyp", "Value Type of Engineering Data Element", 1, str],
         ["engdts", "Engineering Data Element Size", 1, int],
         ["engdatu", "Engineering Data Units", 2, str],
         # Note engdatc is not independent. We have a function below
         # to set this to t.engmtxc[i1]*t.engmtxr[i1]
         ["engdatc", "Engineering Data Count", 8, int],
         ["engdata", "Engineering Data", "f.engdatc[i1]*f.engdts[i1]", None,
          {'field_value_class' : FieldData, 'size_not_updated' : True}],
        ], # End recnt loop
]

TreENGRDA = create_nitf_tre_structure("TreENGRDA",desc,hlp=hlp)

def _summary(self):
    res = six.StringIO()
    print("ENGRDA %s: %d Entries:" \
          % (self.resrc, self.recnt), file=res)
    for i in range(self.recnt):
        print("%d. %s [%d X %d] %s%d" \
              % (i, self.englbl[i], self.engmtxc[i], self.engmtxr[i], self.engtyp[i], self.engdts[i]), file=res)
    return res.getvalue()

def _as_array(self, ind):
    if(self.engtyp[ind] == "B"):
        return (self.engdata[ind], self.engdatu[ind])
    elif(self.engtyp[ind] == "A"):
        return (self.engdata[ind].decode('utf-8'), self.engdatu[ind])
    elif(self.engtyp[ind] == "I"):
        dt = np.dtype('>u%d' % self.engdts[ind])
    elif(self.engtyp[ind] == "S"):
        dt = np.dtype('>i%d' % self.engdts[ind])
    elif(self.engtyp[ind] == "S"):
        dt = np.dtype('>i%d' % self.engdts[ind])
    elif(self.engtyp[ind] == "R"):
        dt = np.dtype('>f%d' % self.engdts[ind])
    elif(self.engtyp[ind] == "C"):
        dt = np.dtype('>c%d' % self.engdts[ind])
    else:
        raise RuntimeError("Unknown engtype: %s" % self.engtyp[ind])
    res = np.frombuffer(self.engdata[ind], dtype=dt)
    res = res.reshape((self.engmtxr[ind], self.engmtxc[ind]))
    return (res, self.engdatu[ind])

# engdatc isn't really independent, so fill this in
def _engdatc_value(self, *key):
    return (self.engmtxc[key]*self.engmtxr[key])

TreENGRDA.engdatc_value = _engdatc_value

TreENGRDA.summary = _summary

# Add or update engineering record. We update if the label is already
# in use, otherwise we add it as a new record.
#
# Note that the type "A" for string and "B" for bytes could be represented
# using the python bytes types. However, as a convention if we get passed
# a str we assume "A", and bytes we assume "B".

def _add_or_update(self, key, data, units):
    keyv = key
    if(not isinstance(keyv, bytes)):
        keyv = key.encode('utf-8')
    i_to_change = -1
    for i in range(self.recnt):
        if(self.englbl[i] == keyv):
            i_to_change = i
    if(i_to_change == -1):
        self.recnt += 1
        i_to_change = self.recnt - 1
    self.englbl[i_to_change] = keyv
    self.engdatu[i_to_change] = units
    is_byte_type = isinstance(data, (bytes, bytearray))
    if(isinstance(data, (bytes, str))):
        self.engmtxc[i_to_change]=len(data)
        self.engmtxr[i_to_change]=1
    elif(len(data.shape) == 1):
        self.engmtxc[i_to_change]=data.shape[0]
        self.engmtxr[i_to_change]=1
    elif(len(data.shape) == 2):
        self.engmtxc[i_to_change]=data.shape[1]
        self.engmtxr[i_to_change]=data.shape[0]
    else:
        raise RuntimeError("data needs to be bytes, or 1d or 2d numpy array")
    if(isinstance(data, str)):
        self.engtyp[i_to_change]="A"
        self.engdts[i_to_change]=1
        self.engdata[i_to_change] = data.encode('utf-8')
    elif(isinstance(data, bytes)):
        self.engtyp[i_to_change]="B"
        self.engdts[i_to_change]=1
        self.engdata[i_to_change] = data
    elif(data.dtype == np.uint8):
        self.engtyp[i_to_change]="I"
        self.engdts[i_to_change]=1
        self.engdata[i_to_change] = data.tobytes()
    elif(data.dtype == np.int8):
        self.engtyp[i_to_change]="S"
        self.engdts[i_to_change]=1
        self.engdata[i_to_change] = data.tobytes()
    elif(data.dtype == np.dtype('<u2') or data.dtype == np.dtype('>u2')):
        self.engtyp[i_to_change]="I"
        self.engdts[i_to_change]=2
        self.engdata[i_to_change] = data.byteswap(">").tobytes()
    elif(data.dtype == np.dtype('<i2') or data.dtype == np.dtype('>i2')):
        self.engtyp[i_to_change]="S"
        self.engdts[i_to_change]=2
        self.engdata[i_to_change] = data.byteswap(">").tobytes()
    elif(data.dtype == np.dtype('<u4') or data.dtype == np.dtype('>u4')):
        self.engtyp[i_to_change]="I"
        self.engdts[i_to_change]=4
        self.engdata[i_to_change] = data.byteswap(">").tobytes()
    elif(data.dtype == np.dtype('<i4') or data.dtype == np.dtype('>i4')):
        self.engtyp[i_to_change]="S"
        self.engdts[i_to_change]=4
        self.engdata[i_to_change] = data.byteswap(">").tobytes()
    elif(data.dtype == np.dtype('<f4') or data.dtype == np.dtype('>f4')):
        self.engtyp[i_to_change]="R"
        self.engdts[i_to_change]=4
        self.engdata[i_to_change] = data.byteswap(">").tobytes()
    elif(data.dtype == np.dtype('<f8') or data.dtype == np.dtype('>f8')):
        self.engtyp[i_to_change]="R"
        self.engdts[i_to_change]=8
        self.engdata[i_to_change] = data.byteswap(">").tobytes()
    elif(data.dtype == np.dtype('<c8') or data.dtype == np.dtype('>c8')):
        self.engtyp[i_to_change]="C"
        self.engdts[i_to_change]=8
        self.engdata[i_to_change] = data.byteswap(">").tobytes()
    else:
        raise RuntimeError("Unrecognized type")

TreENGRDA.add_or_update = _add_or_update

# Give a dict like interface to a ENGRDA
TreENGRDA.__bases__ = (Tre,MutableMapping)

def _len(self):
    return self.recnt

def _getitem(self, key):
    keyv = key
    if(not isinstance(keyv, bytes)):
        keyv = key.encode('utf-8')
    for i in range(self.recnt):
        if(self.englbl[i] == keyv):
            return _as_array(self, i)
    raise KeyError(key)

def _setitem(self, key, v):
    if(len(v) != 2):
        raise RuntimeError("Need to give two value to set in ENGRDA, the data and the units")
    self.add_or_update(key, v[0], v[1])

def _delitem(self, key):
    raise NotImplementedError("Can't delete from ENGRDA")

def _iter(self):
    return ((self.englbl[i], _as_array(self, i)) for i in range(self.recnt))

TreENGRDA.__len__ = _len
TreENGRDA.__getitem__ = _getitem
TreENGRDA.__iter__ = _iter
TreENGRDA.__delitem__ = _delitem
TreENGRDA.__setitem__ = _setitem

def _engrda_as_hash(self):
    '''Return access to all the ENGRDA TREs as a hash on resrc (which should be
    unique). Error occurs if resrc is not unique.'''
    res = {}
    for t in self.tre_list:
        if(t.tre_tag == "ENGRDA"):
            if(t.resrc in res):
                raise RuntimeError("Two ENGRDA TREs have the same resrc value of '%s'" % t.resrc)
            res[t.resrc] = t
    return res

def add_engrda_function(cls):
    cls.engrda = property(_engrda_as_hash, doc=_engrda_as_hash.__doc__)

__all__ = [ "TreENGRDA"]
