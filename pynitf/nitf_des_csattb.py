from __future__ import print_function
from .nitf_field import *
from .nitf_des import *
import six

hlp = '''This is a NITF CSATTB DES. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in a separate DRAFT document for the SNIP standard.
'''

_quat_format = "%+18.15lf"

desc2 =["CSATTB DES",
        ['id', 'Assigned UUID for the DES', 36, str],
        ["numais", "Number of Associated Image Segments", 3, str],
        [["loop", "0 if f.numais == 'ALL' else int(f.numais)"],
         ["aisdlvl", "Associated Image Segment Display Level", 3, int]],
        ['num_assoc_elem', 'Number of Associated Elements', 3, int],
        [['loop', 'f.num_assoc_elem'],
         ['assoc_elem_id', 'UUID of the nth Associated Element', 36, str]],
        ['reservedsubh_len', 'Length of the Reserved Subheader Fields', 4, int],
        ['reservedsubh', 'Reserved for Future Additions to the DES User-Defined Subheader', 'f.reservedsubh_len', None, {'field_value_class' : FieldData}],
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
        ["reserved_len", "Size of the Reserved Field", 5, int],
        ["reserved", "Reserved Data Field", "f.reserved_len", None, {'field_value_class' : FieldData}]
       ]

#print (desc2)

DesCSATTB = create_nitf_des_structure("DesCSATTB", desc2, hlp=hlp)

DesCSATTB.desid = hardcoded_value("DES CSATTB")
DesCSATTB.desver = hardcoded_value("01")

def _summary(self):
    res = six.StringIO()
    print("CSATTB %s:  %d points" % (self.att_type, self.num_att), file=res)
    return res.getvalue()

DesCSATTB.summary = _summary

__all__ = ["DesCSATTB"]
