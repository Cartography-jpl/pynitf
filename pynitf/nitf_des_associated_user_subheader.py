from .nitf_field import FieldStruct, BytesFieldData, FieldStructDiff
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
import uuid
import time

hlp = '''There are a number of NITF DES that have a user subheader to 
associating elements together. This includes the various DES used for
GLAS/GFM. See for example NITF CSATTB DES.

The user subheader is described in a draft document for the SNIP standard.
'''
desc = [['id', 'Assigned UUID for the DES', 36, str],
        ["numais", "Number of Associated Image Segments", 3, str, {"default": "0"}],
        [["loop", "0 if f.numais == 'ALL' else int(f.numais)"],
         ["aisdlvl", "Associated Image Segment Display Level", 3, int]],
        ['num_assoc_elem', 'Number of Associated Elements', 3, int],
        [['loop', 'f.num_assoc_elem'],
         ['assoc_elem_id', 'UUID of the nth Associated Element', 36, str]],
        ['reservedsubh_len', 'Length of the Reserved Subheader Fields', 4, int],
        ['reservedsubh', 'Reserved for Future Additions to the DES User-Defined Subheader', 'f.reservedsubh_len', None, {'field_value_class' : BytesFieldData}]
       ]

class DesAssociatedUserSubheader(FieldStruct):
    __doc__=hlp
    desc=desc

# Some support routines for working with the user header.

def _id(self):
    return self.user_subheader.id

def _id_set(self,v):
    self.user_subheader.id = v
    
def _aisdlvl(self):
    return list(self.user_subheader.aisdlvl)

def _assoc_elem_id(self):
    return list(self.user_subheader.assoc_elem_id)

def _generate_uuid_if_needed(self):
    '''Generate a unique UUID if we don't already have one.'''
    if(self.user_subheader.id == ""):
        self.user_subheader.id = str(uuid.uuid1())
        # Sleep is just a simple way to avoid calling uuid1 too close in
        # time. Since time is one of the components in generating the uuid,
        # if we call too close in time we get the same uuid.
        time.sleep(0.01)

def _add_display_level(self, lvl):
    '''Add a display level. For convenience, we allow this to be added
    multiple times, it only gets written to the DES once
    '''
    for i in range(int(self.user_subheader.numais)):
        if(self.user_subheader.aisdlvl[i] == lvl):
            return
    self.user_subheader.numais = "%03d" % (int(self.user_subheader.numais) + 1)
    self.user_subheader.aisdlvl[int(self.user_subheader.numais) - 1] = lvl

def _add_assoc_elem_id(self, id):
    '''Add a associated element. For convenience, we allow this to be added
    multiple times, it only gets written to the DES once.
    '''
    for i in range(self.user_subheader.num_assoc_elem):
        if(self.user_subheader.assoc_elem_id[i] == id):
            return
    self.user_subheader.num_assoc_elem += 1
    self.user_subheader.assoc_elem_id[self.user_subheader.num_assoc_elem - 1] = id

def _add_assoc_elem(self, f):
    if(hasattr(f, "id")):
        if(hasattr(f, "generate_uuid_if_needed")):
            f.generate_uuid_if_needed()
        self.add_assoc_elem_id(f.id)
    else:
        raise RuntimeError("Don't know how to add the associated element")

def _assoc_elem(self, f):
    '''Find the associated elements in the given NitfFile f. Right now it
    is not clear if we should treat missing associated elements as an
    error or not. So right now we just return a "None" where we don't have
    an associated element'''
    # Put results in a hash. This lets us sort everything at the end so
    # this is in the same order as assoc_elem_id. Not sure if order matters,
    # but for now we'll preserve this
    res = {}
    asid = self.assoc_elem_id
    for dseg in f.des_segment:
        if(hasattr(dseg.des, "id")):
            if(dseg.des.id in asid):
                res[dseg.des.id] = dseg.des
    for iseg in f.image_segment:
        for tre in iseg.find_tre("CSEXRB"):
            if(tre.image_uuid in asid):
                res[tre.image_uuid] = tre
    r = [ res.get(id) for id in asid]
    return r

def _primary_key(self):
    return (self.desid, self.user_subheader.id)

def add_uuid_des_function(cls):
    cls.id = property(_id, _id_set)
    cls.aisdlvl = property(_aisdlvl)
    cls.assoc_elem_id = property(_assoc_elem_id)
    cls.generate_uuid_if_needed = _generate_uuid_if_needed
    cls.add_display_level = _add_display_level
    cls.add_assoc_elem_id = _add_assoc_elem_id
    cls.add_assoc_elem = _add_assoc_elem
    cls.assoc_elem = _assoc_elem
    cls.primary_key = _primary_key

class DesAssociatedUserSubheaderDiff(FieldStructDiff):
    '''Compare two user headers.'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("DesAssociatedUserSubheader", {})

    def handle_diff(self, h1, h2, nitf_diff):
        with nitf_diff.diff_context("DesAssociatedUserSubheader"):
            if(not isinstance(h1, DesAssociatedUserSubheader) or
               not isinstance(h2, DesAssociatedUserSubheader)):
                return (False, None)
            return (True, self.compare_obj(h1, h2, nitf_diff))

NitfDiffHandleSet.add_default_handle(DesAssociatedUserSubheaderDiff())
_default_config = {}
# UUID change each time they are generated, so don't include in
# check
_default_config["exclude"] = ['id', 'assoc_elem_id']
 
NitfDiffHandleSet.default_config["DesAssociatedUserSubheader"] = _default_config

__all__ = ["DesAssociatedUserSubheader", "add_uuid_des_function"]
