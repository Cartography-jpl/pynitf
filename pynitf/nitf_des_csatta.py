from .nitf_field import *
from .nitf_des import *
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
import io

'''WARNING!!! Do NOT use CSATTA. It's been deprecated and it hasn't kept up with the new DES design
It will be fixed eventually and we can use it if we need to for legacy applications'''

hlp = '''This is a NITF CSATTA DES. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in Table A-8, starting page 112.
'''

_quat_format = "%08.5lf"

desc2 =["CSATTA",
        ['att_type', "Type of attitude data being provided", 12, str],
        ['dt_att', "Time interval between attitude reference points", 14, str],
        ['date_att', "Day of First Attitude Reference Point", 8, int],
        ['t0_att', "UTC of First Attitude Reference Point", 13, str],
        ['num_att', "Number of Attitude Reference Points", 5, int],
        [["loop", "f.num_att"],
         ["att_q1", "Quaternion Q1 of Attitude Reference Point", 8, float, {"frmt": _quat_format}],
         ["att_q2", "Quaternion Q2 of Attitude Reference Point", 8, float, {"frmt": _quat_format}],
         ["att_q3", "Quaternion Q3 of Attitude Reference Point", 8, float, {"frmt": _quat_format}],
         ["att_q4", "Quaternion Q4 of Attitude Reference Point", 8, float, {"frmt": _quat_format}],
        ], #end loop
       ]

#print (desc2)

(DesCSATTA, a) = create_nitf_des_structure("DesCSATTA", desc2, None, hlp=hlp)

DesCSATTA.desver = hardcoded_value("01")

def summary(self):
    res = io.StringIO()
    print("CSATTA %s:  %d points" % (self.att_type, self.num_att), file=res)
    return res.getvalue()

DesCSATTA.summary = summary

register_des_class(DesCSATTA)

class CsattaDiff(FieldStructDiff):
    '''Compare two DesCSATTA.'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("DesCSATTA", {})

    def handle_diff(self, h1, h2, nitf_diff):
        with nitf_diff.diff_context("DesCSATTB"):
            if(not isinstance(h1, DesCSATTA) or
               not isinstance(h2, DesCSATTA)):
                return (False, None)
            return (True, self.compare_obj(h1, h2, nitf_diff))

NitfDiffHandleSet.add_default_handle(CsattaDiff())
# No default configuration
_default_config = {}
NitfDiffHandleSet.default_config["DesCSATTB"] = _default_config

__all__ = ["DesCSATTA"]
