from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the MICIDA TRE, Motion Imagery Core Identification

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (NGA.STND.0044_1.3_MIE4NITF Adjudicated v3.pdf), 
available at https://nsgreg.nga.mil/doc/view?i=4754

MICIDA is documented in Table 13.
'''
desc = ["MICIDA",
        ["miis_core_id_version", "MISB ST 1204 Version Number", 2, int, {"frmt": "%02d"}],
        ["num_camera_ids", "Number of MIIS Core Identifiers", 3, int],
        [["loop", "f.num_camera_ids"],
         ["cameras_id", "Camera UUID", 36, str],
         ["core_id_length", "MIIS Core Identifier Length", 3, int],
         ["camera_core_id", "MIIS Core Identifier", "f.core_id_length[i1]", None,
          {'field_value_class' : StringFieldData}],
        ],
]

TreMICIDA = create_nitf_tre_structure("TreMICIDA",desc,hlp=hlp)
TreMICIDA.miis_core_id_version = hardcoded_value(1)

def _summary(self):
    res = six.StringIO()
    print("MICIDA:", file=res)
    print("MISB ST 1204 Version Number: %02d" % (self.miis_core_id_version()), file=res)
    print("Number of MIIS Core Identifiers: %d" % (self.num_camera_ids), file=res)
    for i in range(self.num_camera_ids):
        print("Camera UUID: %s" % (self.cameras_id[i]), file=res)
        print("MIIS Core Identifier Length: %d" % (self.core_id_length[i]), file=res)
        print("MIIS Core Identifier: %s" % (self.camera_core_id[i]), file=res)

    return res.getvalue()

TreMICIDA.summary = _summary

__all__ = [ "TreMICIDA" ]
