from .nitf_field import BytesFieldData, FieldStructDiff
from .nitf_des import NitfDesFieldStruct
from .nitf_segment_data_handle import NitfSegmentDataHandleSet
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
from .nitf_des_associated_user_subheader import (add_uuid_des_function,
                                                 DesAssociatedUserSubheader)
from .nitf_segment_user_subheader_handle import desid_to_user_subheader_handle
import io

hlp = '''This is a NITF CSEPHB DES. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in a separate DRAFT document for the SNIP standard.
'''

_eph_format = "%+012.2lf"

desc =[['qual_flag_eph', 'Ephemeris Data Quality Flag', 1, int],
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
        ["reserved_len", "Size of the Reserved Field", 9, int],
        ["reserved", "Reserved Data Field", "f.reserved_len", None, {'field_value_class' : BytesFieldData}]
       ]

class DesCSEPHB(NitfDesFieldStruct):
    __doc__ = hlp
    desc = desc
    des_tag = "CSEPHB"
    des_ver = 1
    uh_class = DesAssociatedUserSubheader
    def summary(self):
        res = io.StringIO()
        print("CSEPHB %s:  %d points" % (self.ephem_flag, self.num_ephem),
              file=res)
        return res.getvalue()

desid_to_user_subheader_handle.add_des_user_subheader("CSEPHB",
                      DesAssociatedUserSubheader)
add_uuid_des_function(DesCSEPHB)    
NitfSegmentDataHandleSet.add_default_handle(DesCSEPHB)

class CsephbDiff(FieldStructDiff):
    '''Compare two DesCSEPHB.'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("DesCSEPHB", {})

    def handle_diff(self, h1, h2, nitf_diff):
        with nitf_diff.diff_context("DesCSEPHB"):
            if(not isinstance(h1, DesCSEPHB) or
               not isinstance(h2, DesCSEPHB)):
                return (False, None)
            return (True, self.compare_obj(h1, h2, nitf_diff))

NitfDiffHandleSet.add_default_handle(CsephbDiff())

# No default configuration

_default_config = {}
NitfDiffHandleSet.default_config["DesCSEPHB"] = _default_config

__all__ = ["DesCSEPHB", ]
