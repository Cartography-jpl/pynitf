from __future__ import print_function
from .nitf_field import *
from .nitf_des import *
import time
import uuid
import six

hlp = '''This is a NITF CSATTB DES. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in a separate DRAFT document for the SNIP standard.
'''

_quat_format = "%+18.15lf"

desc2 =["CSATTB",
        ['qual_flag_att', 'Attitude Data Quality Flag', 1, int],
        ['interp_type_att', 'Interpolation Type', 1, int],
        ['interp_order_att', 'Order of Lagrange Interpolation Polynomials', 1, int, {'condition': 'f.interp_type_att==2'}],
        ['att_type', "Attitude Type", 1, int],
        ['eci_ecf_att', 'Coordinate Reference Frame Flag', 1, int],
        ['dt_att', "Time interval between attitude reference points", 13, float, {'frmt': '%013.9lf'}],
        ['date_att', "Day of First Attitude Reference Point", 8, int],
        ['t0_att', "UTC Timestamp of First Attitude Reference Point", 16, float, {'frmt': '%016.9lf'}],
        ['num_att', "Number of Attitude Reference Points", 5, int],
        [["loop", "f.num_att"],
         ["q1", "Quaternion Q1 of Attitude Reference Point", 18, float, {"frmt": _quat_format}],
         ["q2", "Quaternion Q2 of Attitude Reference Point", 18, float, {"frmt": _quat_format}],
         ["q3", "Quaternion Q3 of Attitude Reference Point", 18, float, {"frmt": _quat_format}],
         ["q4", "Quaternion Q4 of Attitude Reference Point", 18, float, {"frmt": _quat_format}],
        ], #end loop
        ["reserved_len", "Size of the Reserved Field", 9, int],
        ["reserved", "Reserved Data Field", "f.reserved_len", None, {'field_value_class' : FieldData}]
       ]

#print (desc2)

udsh = [['id', 'Assigned UUID for the DES', 36, str],
        ["numais", "Number of Associated Image Segments", 3, str, {"default": "0"}],
        [["loop", "0 if f.numais == 'ALL' else int(f.numais)"],
         ["aisdlvl", "Associated Image Segment Display Level", 3, int]],
        ['num_assoc_elem', 'Number of Associated Elements', 3, int],
        [['loop', 'f.num_assoc_elem'],
         ['assoc_elem_id', 'UUID of the nth Associated Element', 36, str]],
        ['reservedsubh_len', 'Length of the Reserved Subheader Fields', 4, int],
        ['reservedsubh', 'Reserved for Future Additions to the DES User-Defined Subheader', 'f.reservedsubh_len', None, {'field_value_class' : FieldData}]
       ]

(DesCSATTB, DesCSATTB_UH) = create_nitf_des_structure("DesCSATTB", desc2, udsh, hlp=hlp)

DesCSATTB.desid = hardcoded_value("CSATTB")
DesCSATTB.desver = hardcoded_value("01")

def _summary(self):
    res = six.StringIO()
    print("CSATTB %s:  %d points" % (self.att_type, self.num_att), file=res)
    return res.getvalue()

DesCSATTB.summary = _summary

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

def add_uuid_des_function(cls):
    cls.id = property(_id, _id_set)
    cls.aisdlvl = property(_aisdlvl)
    cls.assoc_elem_id = property(_assoc_elem_id)
    cls.generate_uuid_if_needed = _generate_uuid_if_needed
    cls.add_display_level = _add_display_level
    cls.add_assoc_elem_id = _add_assoc_elem_id
    cls.add_assoc_elem = _add_assoc_elem
    cls.assoc_elem = _assoc_elem

add_uuid_des_function(DesCSATTB)    
register_des_class(DesCSATTB)
__all__ = ["DesCSATTB", "DesCSATTB_UH", "add_uuid_des_function"]
