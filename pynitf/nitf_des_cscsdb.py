from __future__ import print_function
from .nitf_field import *
from .nitf_des import *
from .nitf_des_csattb import udsh, add_uuid_des_function
import six

hlp = '''This is a NITF CSCSDB DES. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in a separate DRAFT document for the SNIP standard.
'''

_quat_format = "%+18.15lf"

desc2 =["CSCSDB",
        ['cov_version_date', 'Covariance Version Date', 8, str],
        ['core_sets', "Number of Core Sets", 1, int],
#        [['loop', 'f.core_sets'],
#         ["ref_frame_position", "Reference Frame for Position Coordinate Syste of the nth Core Set", 1, int],
#         ["ref_frame_attitude", "Reference Frame for Attitude Coordinate Syste of the nth Core Set", 1, int],
#         ["num_groups", "Number of Interdependent Sensor Error Parameter Groups of the nth Core Set", 1, int],
#         ]
]        

#print (desc2)

# udsh here is a from nitf_des_csattb, since the same user defined subheader
# is used for both
# data_after_allowed temporary until we fill in all the fields
(DesCSCSDB, DesCSCSDB_UH) = create_nitf_des_structure("DesCSCSDB", desc2, udsh, hlp=hlp, data_after_allowed=True, data_copy=True)

DesCSCSDB.desid = hardcoded_value("CSCSDB")
DesCSCSDB.desver = hardcoded_value("01")

def _summary(self):
    res = six.StringIO()
    print("CSCSDB", file=res)
    return res.getvalue()

DesCSCSDB.summary = _summary

add_uuid_des_function(DesCSCSDB)    
register_des_class(DesCSCSDB)
__all__ = ["DesCSCSDB", "DesCSCSDB_UH"]
