from __future__ import print_function
from .nitf_field import *
from .nitf_des import *
import six

hlp = '''This is a NITF CSEPHB DES. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in a separate DRAFT document for the SNIP standard.
'''

_eph_format = "%+012.2lf"

desc2 =["CSEPHB",
        ['id', 'Assigned UUID for the DES', 36, str],
        ["numais", "Number of Associated Image Segments", 3, str],
        [["loop", "0 if f.numais == 'ALL' else int(f.numais)"],
         ["aisdlvl", "Associated Image Segment Display Level", 3, int]],
        ['num_assoc_elem', 'Number of Associated Elements', 3, int],
        [['loop', 'f.num_assoc_elem'],
         ['assoc_elem_id', 'UUID of the nth Associated Element', 36, str]],
        ['reservedsubh_len', 'Length of the Reserved Subheader Fields', 4, int],
        ['reservedsubh', 'Reserved for Future Additions to the DES User-Defined Subheader', 'f.reservedsubh_len', None, {'field_value_class' : FieldData}],
        ['qual_flag_eph', 'Ephemeris Data Quality Flag', 1, int],
        ['interp_type_eph', 'Interpolation Type', 1, int],
        ['interp_order_eph', 'Order of Lagrange Interpolation Polynomials', 1, int, {'condition': 'f.interp_type_eph==2'}],
        ['ephem_flag', "Ephemeris Source Type", 1, int],
        ['eci_ecf_ephem', 'Coordinate Reference Frame Flag', 1, int],
        ['dt_ephem', "Time interval between Ephemeris Vectors", 13, float, {'frmt': '%013.9lf'}],
        ['date_ephem', "Date of First Ephemeris Vector", 8, int],
        ['t0_ephem', "UTC Timestamp of First Ephemeris Vector", 16, float, {'frmt': '%016.9lf'}],
        ['num_ephem', "Number of Ephemeris Vectors", 5, int],
        [["loop", "f.num_ephem"],
         ["ephem_x", "X-Coordinate", 12, float, {"frmt": _eph_format}],
         ["ephem_y", "Y-Coordinate", 12, float, {"frmt": _eph_format}],
         ["ephem_z", "Z-Coordinate", 12, float, {"frmt": _eph_format}],
        ], #end loop
        ["reserved_len", "Size of the Reserved Field", 5, int],
        ["reserved", "Reserved Data Field", "f.reserved_len", None, {'field_value_class' : FieldData}]
       ]

#print (desc2)

DesCSEPHB = create_nitf_des_structure("DesCSEPHB", desc2, hlp=hlp)

DesCSEPHB.desid = hardcoded_value("DES CSEPHB")
DesCSEPHB.desver = hardcoded_value("01")

def _summary(self):
    res = six.StringIO()
    print("CSEPHB %s:  %d points" % (self.ephem_flag, self.num_ephem), file=res)
    return res.getvalue()

DesCSEPHB.summary = _summary

__all__ = ["DesCSEPHB"]
