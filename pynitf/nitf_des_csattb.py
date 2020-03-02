from .nitf_field import BytesFieldData, FieldStructDiff
from .nitf_des import NitfDesFieldStruct
from .nitf_segment_data_handle import NitfSegmentDataHandleSet
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
from .nitf_des_associated_user_subheader import (add_uuid_des_function,
                                                 DesAssociatedUserSubheader)
from .nitf_segment_user_subheader_handle import desid_to_user_subheader_handle
import io

hlp = '''This is a NITF CSATTB DES. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in a separate DRAFT document for the SNIP standard.
'''

_quat_format = "%+18.15lf"

desc =[['qual_flag_att', 'Attitude Data Quality Flag', 1, int],
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
        ["reserved", "Reserved Data Field", "f.reserved_len", None, {'field_value_class' : BytesFieldData}]
       ]

class DesCSATTB(NitfDesFieldStruct):
    __doc__ = hlp
    desc = desc
    des_tag = "CSATTB"
    des_ver = 1
    uh_class = DesAssociatedUserSubheader
    def summary(self):
        res = io.StringIO()
        print("CSATTB %s:  %d points" % (self.att_type, self.num_att), file=res)
        return res.getvalue()
    
desid_to_user_subheader_handle.add_des_user_subheader("CSATTB",
                      DesAssociatedUserSubheader)
add_uuid_des_function(DesCSATTB)    
NitfSegmentDataHandleSet.add_default_handle(DesCSATTB)

class CsattbDiff(FieldStructDiff):
    '''Compare two DesCSATTB.'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("DesCSATTB", {})

    def handle_diff(self, h1, h2, nitf_diff):
        with nitf_diff.diff_context("DesCSATTB"):
            if(not isinstance(h1, DesCSATTB) or
               not isinstance(h2, DesCSATTB)):
                return (False, None)
            return (True, self.compare_obj(h1, h2, nitf_diff))

NitfDiffHandleSet.add_default_handle(CsattbDiff())

# No default configuration

_default_config = {}
NitfDiffHandleSet.default_config["DesCSATTB"] = _default_config

__all__ = ["DesCSATTB", ]
