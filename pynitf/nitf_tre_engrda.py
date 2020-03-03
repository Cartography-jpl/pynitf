from .nitf_field import StringFieldData, BytesFieldData, FieldData
from .nitf_tre import Tre, tre_tag_to_cls
import io
from collections.abc import MutableMapping
import numpy as np

class ENGRDAFieldData(FieldData):
    def pack(self, key, data):
        '''Return bytes representing the given value. Note that we 
        update engtyp and engdts at the same time.'''
        if(isinstance(data, str)):
            self.fs.engtyp[key]="A"
            self.fs.engdts[key]=1
            return data.encode('utf-8')
        elif(isinstance(data, bytes)):
            self.fs.engtyp[key]="B"
            self.fs.engdts[key]=1
            return data
        elif(data.dtype == np.uint8):
            self.fs.engtyp[key]="I"
            self.fs.engdts[key]=1
            return data.tobytes()
        elif(data.dtype == np.int8):
            self.fs.engtyp[key]="S"
            self.fs.engdts[key]=1
            return data.tobytes()
        elif(data.dtype == np.dtype('<u2') or data.dtype == np.dtype('>u2')):
            self.fs.engtyp[key]="I"
            self.fs.engdts[key]=2
            return data.byteswap(">").tobytes()
        elif(data.dtype == np.dtype('<i2') or data.dtype == np.dtype('>i2')):
            self.fs.engtyp[key]="S"
            self.fs.engdts[key]=2
            return data.byteswap(">").tobytes()
        elif(data.dtype == np.dtype('<u4') or data.dtype == np.dtype('>u4')):
            self.fs.engtyp[key]="I"
            self.fs.engdts[key]=4
            return data.byteswap(">").tobytes()
        elif(data.dtype == np.dtype('<i4') or data.dtype == np.dtype('>i4')):
            self.fs.engtyp[key]="S"
            self.fs.engdts[key]=4
            return data.byteswap(">").tobytes()
        elif(data.dtype == np.dtype('<f4') or data.dtype == np.dtype('>f4')):
            self.fs.engtyp[key]="R"
            self.fs.engdts[key]=4
            return data.byteswap(">").tobytes()
        elif(data.dtype == np.dtype('<f8') or data.dtype == np.dtype('>f8')):
            self.fs.engtyp[key]="R"
            self.fs.engdts[key]=8
            return data.byteswap(">").tobytes()
        elif(data.dtype == np.dtype('<c8') or data.dtype == np.dtype('>c8')):
            self.fs.engtyp[key]="C"
            self.fs.engdts[key]=8
            return data.byteswap(">").tobytes()
        else:
            raise RuntimeError("Unrecognized type")

    def unpack(self, key, bdata):
        '''Unpack the bytes bdate and return value.'''
        typ = self.fs.engtyp[key]
        dts = self.fs.engdts[key]
        if(typ == "A" and dts == 1):
            return bdata.decode('utf-8')
        elif(typ == "B" and dts == 1):
            return bdata
        elif(typ == "I"):
            dt = np.dtype('>u%d' % dts)
        elif(typ == "S"):
            dt = np.dtype('>i%d' % dts)
        elif(typ == "R"):
            dt = np.dtype('>f%d' % dts)
        elif(typ == "C"):
            dt = np.dtype('>c%d' % dts)
        else:
            raise RuntimeError("Unknown engtype: %s" % typ)
        res = np.frombuffer(bdata, dtype=dt)
        res = res.reshape((self.fs.engmtxr[key], self.fs.engmtxc[key]))
        return res

    def get_print(self, key):
        t = self[key]
        if(t is None):
            return "Not used"
        if(hasattr(t, "shape") and t.shape == (1,1)):
            return "%s" % (t[0,0])
        elif(hasattr(t, "shape") and t.shape[0] == 1):
            return "%s" % (t[0,:])
        return "%s" % t

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
desc = [["resrc", "Unique Source System Name", 20, str],
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
         ["engdatc", "Engineering Data Count", 8, int,
          {"value" : lambda fs, key : fs.engmtxc[key] * fs.engmtxr[key]}],
         ["engdata", "Engineering Data", "f.engdatc[i1]*f.engdts[i1]", None,
          {'field_value_class' : ENGRDAFieldData, 'size_not_updated' : True}],
        ], # End recnt loop
]

class TreENGRDA(Tre,MutableMapping):
    __doc__ = hlp
    desc = desc
    tre_tag = "ENGRDA"
    def summary(self):
        res = io.StringIO()
        print("TRE - ENGRDA %s: %d Entries:"
              % (self.resrc, self.recnt), file=res)
        return res.getvalue()

    def add_or_update(self, key, data, units):
        '''Add or update engineering record. We update if the label 
        is already in use, otherwise we add it as a new record.
    
        Note that the type "A" for string and "B" for bytes could
        be represented using the python bytes types. However, as a
        convention if we get passed a str we assume "A", and bytes
        we assume "B".'''
        keyv = key
        if(not isinstance(keyv, str)):
            keyv = key.decode('utf-8')
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
        self.engdata[i_to_change] = data

    def _as_array(self, ind):
        return (self.engdata[ind], self.engdatu[ind])
    
    def __len__(self):
        return self.recnt

    def __getitem__(self, key):
        keyv = key
        if(not isinstance(keyv, str)):
            keyv = key.decode('utf-8')
        for i in range(self.recnt):
            if(self.englbl[i] == keyv):
                return self._as_array(i)
        raise KeyError(key)

    def __setitem__(self, key, v):
        if(len(v) != 2):
            raise RuntimeError("Need to give two value to set in ENGRDA, the data and the units")
        self.add_or_update(key, v[0], v[1])

    def __delitem__(self, key):
        raise NotImplementedError("Can't delete from ENGRDA")

    def __iter__(self):
        return ((self.englbl[i], _as_array(self, i)) for i in range(self.recnt))

tre_tag_to_cls.add_cls(TreENGRDA)    

#def _getEngLblByIndex(self, i):
#    return self.englbl[i]

#TreENGRDA.getEngLblByIndex = _getEngLblByIndex

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
