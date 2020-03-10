# Note when importing TREs that much of the documentation is in PDF tables.
# You can't easily paste this directly to emacs. But you can import to Excel.
# To do this, cute and paste the table into *Word*, and then cut and paste
# from word to Excel. For some reason, you can't go directly to Excel. You
# can then cut and paste from excel to emacs

from .nitf_field import FieldStruct, FieldStructDiff
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
import copy
import io
import logging
import warnings

class TreWarning(UserWarning):
    '''Warning specific to trouble reading a TRE'''
    pass

class Tre(FieldStruct):
    '''Add a little extra structure unique to Tres'''
    tre_implementation_field = None
    tre_implementation_class = None
    def cetag_value(self):
        return self.tre_tag
    def cel_value(self):
        return len(self.tre_bytes())
    def tre_bytes(self):
        '''All of the TRE expect for the front two cetag and cel fields'''
        if(self.tre_implementation_field):
            t = getattr(self, self.tre_implementation_field).tre_string()
            if(isinstance(t, bytes)):
                return t
            return t.encode("utf-8")
        else:
            fh = io.BytesIO()
            super().write_to_file(fh)
            return fh.getvalue()
    def read_from_tre_bytes(self, bt, nitf_literal=False):
        if(self.tre_implementation_field):
            t = bt
            if not isinstance(t, str):
                t = t.decode("utf-8")
            setattr(self, self.tre_implementation_field, self.tre_implementation_class.read_tre_string(t))
            self.update_raw_field()
        else:
            fh = io.BytesIO(bt)
            super().read_from_file(fh, nitf_literal=nitf_literal)
    def read_from_file(self, fh):
        tag = fh.read(6).rstrip().decode("utf-8")
        if(tag != self.tre_tag):
            raise RuntimeError("Expected TRE %s but got %s" % (self.tre_tag, tag))
        cel = int(fh.read(5))
        if(self.tre_implementation_field):
            self.read_from_tre_bytes(fh.read(cel))
        else:
            st = fh.tell()
            super().read_from_file(fh)
            sz = fh.tell() - st
            if(sz != cel):
                raise RuntimeError("TRE length was expected to be %d but was actually %d" % (cel, sz))
    def write_to_file(self, fh):
        fh.write("{:6s}".format(self.cetag_value()).encode("utf-8"))
        t = self.tre_bytes()
        v = len(t)
        if(v > 99999):
            raise RuntimeError("TRE string is too long at size %d" % v)
        fh.write("{:0>5d}".format(v).encode("utf-8"))
        fh.write(t)
    def str_hook(self, fh):
        '''Convenient to have a place to add stuff in __str__ for derived
        classes. This gets called after the TRE name is written, but before
        any fields. Default is to do nothing, but derived classes can 
        override this if desired.'''
        if(self.tre_implementation_field):
            print("Object associated with TRE:", file=fh)
            print(getattr(self, self.tre_implementation_field), file=fh)
            print("Raw fields:", file=fh)
            
    def __str__(self):
        '''Text description of structure, e.g., something you can print
        out.'''
        res = io.StringIO()
        print("TRE - %s" % self.tre_tag, file=res)
        self.str_hook(res)
        print(super().__str__(), file=res)
        return res.getvalue()

    def summary(self):
        res = io.StringIO()
        print("TRE - %s" % self.tre_tag, file=res)
        return res.getvalue()
    
    def update_raw_field(self):
        '''Update the raw fields after a change to tre_implementation_field'''
        fh = io.BytesIO(self.tre_bytes())
        super().read_from_file(fh)
        
class TreUnknown(Tre):
    '''The is a general class to handle TREs that we don't have another 
    handler for. It just reports the tre string.'''
    def __init__(self, tre_tag):
        super().__init__(description = [])
        self.tre_tag = tre_tag
        self.tre_bytes = b''
    def cetag_value(self):
        return self.tre_tag
    def cel_value(self):
        return len(self.tre_bytes())
    def read_from_file(self, fh):
        self.tre_tag = fh.read(6).rstrip().decode("utf-8")
        cel = int(fh.read(5))
        self.tre_bytes = fh.read(cel)
    def write_to_file(self, fh):
        fh.write("{:6s}".format(self.cetag_value()).encode("utf-8"))
        v = len(self.tre_bytes)
        if(v > 99999):
            raise RuntimeError("TRE string is too long")
        fh.write("{:0>5d}".format(v).encode("utf-8"))
        fh.write(self.tre_bytes)
    def __str__(self):
        '''Text description of structure, e.g., something you can print
        out.'''
        res = io.StringIO()
        print("TRE - %s" % self.tre_tag, file=res)
        print( "   String: %s" % self.tre_bytes, file=res)
        return res.getvalue()
    def __eq__(self, other):
        return self.tre_tag == other.tre_tag and self.tre_bytes == other.tre_bytes

class TreTagToCls(object):
    '''Simple class to map a TRE tag name to the TRE class we have for
    handling it'''
    def __init__(self):
        self.tre_to_cls = {}

    def tre_object(self, tre_name):
        '''Return a TRE object that can be used to read or write the given tre
        name, or a TreUnknown if we don't have that registered.'''
        if(tre_name in self.tre_to_cls):
            return self.tre_to_cls[tre_name]()
        return TreUnknown(tre_name)

    def add_cls(self, cls):
        t = cls.tre_tag
        if(isinstance(t, str)):
            t = t.encode("utf-8")
        self.tre_to_cls[t] = cls

tre_tag_to_cls = TreTagToCls()        

def read_tre(header, des_list, field_list = []):
    '''This reads a TRE for a particular type of header (e.g., NitfFileHeader,
    NitfImageSubheader). The reading is complicated. There are one or
    more base field names to check, each has three fields,
    e.g. udhdl, udhofl, udhd or the file header.
    Each of these fields may or may not have TRE data. In addition, there
    is an "overflow" indicator which points to a TRE_OVERFLOW DES to read 
    additional TREs. This function processes through this logic and 
    reads all the TREs, returning a (possibly empty) list of TREs.'''
    tre_list = []
    for h_len, h_ofl, h_data in field_list:
        if(getattr(header, h_len) > 0):
            des_index = getattr(header, h_ofl)
            if(des_index > 0):
                # des_index is 1 based, so subtract 1 to get the des
                desseg = des_list[getattr(header, h_ofl)-1]
                t = read_tre_data(desseg.des.data)
                tre_list.extend(t)
            t = read_tre_data(getattr(header, h_data))
            tre_list.extend(t)
    return tre_list

def prepare_tre_write(tre_list, header, des_list, field_list = [],
                      seg_index = 0):
    '''This prepares TREs for writing, placing them in the right place
    in a header and/or creating TRE_OVERFLOW DES. This is the reverse
    of read_tre, the field_list should be the same as for that.

    The seg_index should be the normal 0 based index used in python for
    lists. We internally translate this too and from the 1 based indexing
    used in the NITF file.'''
    head_fh = [io.BytesIO() for i in range(len(field_list))]
    des_fh = io.BytesIO()
    for tre in tre_list:
        fht = io.BytesIO()
        tre.write_to_file(fht)
        t = fht.getvalue()
        wrote = False
        for fh in head_fh:
            if(len(fh.getvalue()) + len(t) < 99999-3):
                fh.write(t)
                wrote = True
                break
        if(not wrote):
            des_fh.write(t)
    for i in range(len(field_list)):
        h_len, h_offl, h_data = field_list[i]
        if(getattr(header, h_len) > 0):
            # Clear out any overflow TREs that may have been present
            # from earlier write. We recreate these, so we don't want
            # them
            setattr(header, h_offl, 0)
        if(len(head_fh[i].getvalue()) > 0):
            setattr(header, h_data, head_fh[i].getvalue())
    if(len(des_fh.getvalue()) > 0):
        # We have a circular dependency. It is actually real, and isn't
        # something we particularly need to break. Instead, work around by
        # delaying the import
        from .nitf_file import NitfDesSegment
        from .nitf_des import TreOverflow
        # We could in principle have multiple overflow TREs, one for
        # each row in the field_list. For now, we restrict this to only
        # the first row
        h_len, h_offl, h_data = field_list[0]
        des = TreOverflow(seg_index=seg_index, overflow=h_data)
        desseg = NitfDesSegment(des)
        des.data = des_fh.getvalue()
        des_list.append(desseg)
        setattr(header, h_offl, len(des_list))
    
def read_tre_data(data):
    '''Read a blob of data, and translate into a series of TREs'''
    fh = io.BytesIO(data)
    res = []
    while True:
        st = fh.tell()
        tre_name = fh.read(6)
        if(len(tre_name) == 0):
            break
        if(len(tre_name) != 6):
            raise RuntimeError("Not enough data to get TRE name.")
        try:
            fh.seek(st)
            t = tre_tag_to_cls.tre_object(tre_name)
            t.read_from_file(fh)
            res.append(t)
        except Exception as e:
            warnings.warn("Trouble reading TRE " + tre_name.decode("utf-8") +
                          " " + str(e) +
                          ", treating as a TreUnknown so we can continue.",
                          TreWarning)
            fh.seek(st)
            t = TreUnknown(tre_name)
            t.read_from_file(fh)
            res.append(t)
    return res
    
def _find_tre(self, tre_tag):
    return [t for t in self.tre_list if t.tre_tag == tre_tag]

def _find_one_tre(self, tre_tag):
    '''Find the given TRE. If not found, return None. If found, return it,
    if more than one found, return an error'''
    t = _find_tre(self, tre_tag)
    if(len(t) == 0):
        return None
    if(len(t) == 1):
        return t[0]
    raise RuntimeError("Found more than one %s TRE" % tre_tag)

def _find_exactly_one_tre(self, tre_tag):
    '''Like find_one_tre, but not finding the TRE is treated as an error'''
    t = _find_one_tre(self, tre_tag)
    if(t is None):
        raise RuntimeError("The %s TRE is not found" % tre_tag)
    return t

def add_find_tre_function(cls):
    cls.find_tre = _find_tre
    cls.find_one_tre = _find_one_tre
    cls.find_exactly_one_tre = _find_exactly_one_tre

logger = logging.getLogger('nitf_diff')
class TreDiff(FieldStructDiff):
    '''Compare two TREs.'''
    def configuration(self, nitf_diff):
        return self._config
    def handle_diff(self, h1, h2, nitf_diff):
        if(not isinstance(h1, Tre) or
           not isinstance(h2, Tre)):
            return (False, None)
        if(h1.tre_tag != h2.tre_tag):
            logger.difference("TREs tags don't match. TRE 1 '%s' and TRE 2 '%s'",
                              h1.tre_tag, h2.tre_tag)
            return (True, False)
        self._config = nitf_diff.config.get("TRE", {}).get(h1.tre_tag, {})
        with nitf_diff.diff_context("TRE '%s'" % h1.tre_tag, add_text = True):
            return (True, self.compare_obj(h1, h2, nitf_diff))
        
NitfDiffHandleSet.add_default_handle(TreDiff())
NitfDiffHandleSet.default_config["TRE"] = {}
        
class TreUnknownDiff(FieldStructDiff):
    '''Compare two unknown TREs.'''
    def handle_diff(self, h1, h2, nitf_diff):
        if(not isinstance(h1, TreUnknown) or
           not isinstance(h2, TreUnknown)):
            return (False, None)
        if(h1.tre_tag != h2.tre_tag):
            logger.difference("TREs tags don't match. TRE 1 '%s' and TRE 2 '%s'",
                              h1.tre_tag, h2.tre_tag)
            return (True, False)
        if(h1.tre_bytes != h2.tre_bytes):
            logger.difference("TREs bytes don't match. TRE 1 '%s' and TRE 2 '%s'",
                              h1.tre_bytes.decode('utf-8'),
                              h2.tre_bytes.decode('utf-8'))
            return (True, False)
        return (True, True)

# Look for TreUnknown first, before handling the generic TRE case    
NitfDiffHandleSet.add_default_handle(TreUnknownDiff(), priority_order = 1)
    
__all__ = [ "TreUnknown", "TreDiff", "Tre", "TreWarning",
            "tre_tag_to_cls",
            "read_tre", "prepare_tre_write", "read_tre_data",
            "add_find_tre_function"]

