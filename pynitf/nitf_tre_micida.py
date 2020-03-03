from .nitf_field import StringFieldData
from .nitf_tre import Tre, tre_tag_to_cls
import io

hlp = '''This is the MICIDA TRE, Motion Imagery Core Identification

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (NGA.STND.0044_1.3_MIE4NITF Adjudicated v3.pdf), 
available at https://nsgreg.nga.mil/doc/view?i=4754

MICIDA is documented in Table 13.
'''
desc = [["miis_core_id_version", "MISB ST 1204 Version Number", 2, int,
         {"frmt": "%02d", "default" : 1, "hardcoded_value" : True}],
        ["num_camera_ids", "Number of MIIS Core Identifiers", 3, int],
        [["loop", "f.num_camera_ids"],
         ["cameras_id", "Camera UUID", 36, str],
         ["core_id_length", "MIIS Core Identifier Length", 3, int],
         ["camera_core_id", "MIIS Core Identifier", "f.core_id_length[i1]", None,
          {'field_value_class' : StringFieldData}],
        ],
]

class TreMICIDA(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "MICIDA"

tre_tag_to_cls.add_cls(TreMICIDA)    

__all__ = [ "TreMICIDA", ]
