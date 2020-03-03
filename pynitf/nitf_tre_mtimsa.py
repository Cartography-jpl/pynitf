from .nitf_field import IntFieldData
from .nitf_tre import Tre, tre_tag_to_cls
import io

hlp = '''This is the MTIMSA TRE, Motion Imagery File

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (NGA.STND.0044_1.3_MIE4NITF Adjudicated v3.pdf), 
available at https://nsgreg.nga.mil/doc/view?i=4754

MTIMSA is documented in Table 18.
'''
desc = [["image_seg_index", "Image Segment Index", 3, int],
        ["geocoords_static", "Static GeoCoords Flag", 2, int],
        ["layer_id", "Layer Identifier", 36, str],
        ["camera_set_index", "Camera Set Index", 3, int],
        ["camera_id", "Camera UUID", 36, str],
        ["time_interval_index", "Time Interval Index", 6, int],
        ["temp_block_index", "Temporal Block Index", 3, int],
        ["nominal_frame_rate", "Nominal Frame Rate", 13, float],
        ["reference_frame_num", "Absolute Frame Number", 9, int],
        ["base_timestamp", "Base Timestamp", 24, str],
        ["dt_multiplier", "Frame Delta Time", 8, None,
         {'field_value_class' : IntFieldData, 'size_not_updated' : True,
          'signed' : False}],
        ["dt_size", "Size of DT Values (bytes)", 1, None,
         {'field_value_class' : IntFieldData, 'size_not_updated' : True,
          'signed' : False}],
        ["number_frames", "Number of Frames", 4, None,
         {'field_value_class' : IntFieldData, 'size_not_updated' : True,
          'signed' : False}],
        ["number_dt", "Number of DELTA_TIME Values", 4, None,
         {'field_value_class' : IntFieldData, 'size_not_updated' : True,
          'signed' : False}],
        [["loop", "f.number_dt"],
         ["dt", "Number of Delta Time Units", "f.dt_size", None,
          {'field_value_class' : IntFieldData, 'size_not_updated' : True,
           'signed' : False}],
        ],
]

class TreMTIMSA(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "MTIMSA"

tre_tag_to_cls.add_cls(TreMTIMSA)    

__all__ = [ "TreMTIMSA" ]
