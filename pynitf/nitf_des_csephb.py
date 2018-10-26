from __future__ import print_function
from .nitf_field import *
from .nitf_des import *
from .nitf_des_csattb import udsh
import six

hlp = '''This is a NITF CSEPHB DES. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in a separate DRAFT document for the SNIP standard.
'''

_eph_format = "%+012.2lf"

desc2 =["CSEPHB DES",
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

# udsh here is a from nitf_des_csattb, since the same user defined subheader
# is used for both
(DesCSEPHB, DesCSEPHB_UH) = create_nitf_des_structure("DesCSEPHB", desc2, udsh, hlp=hlp)

DesCSEPHB.desid = hardcoded_value("DES CSEPHB")
DesCSEPHB.desver = hardcoded_value("01")

def _summary(self):
    res = six.StringIO()
    print("CSEPHB %s:  %d points" % (self.ephem_flag, self.num_ephem), file=res)
    return res.getvalue()

DesCSEPHB.summary = _summary

register_des_class(DesCSEPHB)

__all__ = ["DesCSEPHB", "DesCSEPHB_UH"]
