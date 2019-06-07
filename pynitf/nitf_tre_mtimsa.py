from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six
from struct import *

hlp = '''This is the MTIMSA TRE, Motion Imagery File

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (NGA.STND.0044_1.3_MIE4NITF Adjudicated v3.pdf), 
available at https://nsgreg.nga.mil/doc/view?i=4754

MTIMSA is documented in Table 18.
'''
desc = ["MTIMSA",
        ["image_seg_index", "Image Segment Index", 3, int],
        ["geocoords_static", "Static GeoCoords Flag", 2, int],
        ["layer_id", "Layer Identifier", 36, str],
        ["camera_set_index", "Camera Set Index", 3, int],
        ["camera_id", "Camera UUID", 36, str],
        ["time_interval_index", "Time Interval Index", 6, int],
        ["temp_block_index", "Temporal Block Index", 3, int],
        ["nominal_frame_rate", "Nominal Frame Rate", 13, float],
        ["reference_frame_num", "Absolute Frame Number", 9, int],
        ["base_timestamp", "Base Timestamp", 24, str],
        ["dt_multiplier", "Frame Delta Time", 8, None, {'field_value_class' : IntFieldData, 'size_not_updated' : True, 'signed' : False}],
        ["dt_size", "Size of DT Values (bytes)", 1, None, {'field_value_class' : IntFieldData, 'size_not_updated' : True, 'signed' : False}],
        ["number_frames", "Number of Frames", 4, None, {'field_value_class' : IntFieldData, 'size_not_updated' : True, 'signed' : False}],
        ["number_dt", "Number of DELTA_TIME Values", 4, None, {'field_value_class' : IntFieldData, 'size_not_updated' : True, 'signed' : False}],
        [["loop", "f.number_dt"],
         ["dt", "Number of Delta Time Units", "f.dt_size", None,
          {'field_value_class' : IntFieldData, 'size_not_updated' : True, 'signed' : False}],
        ],
]

TreMTIMSA = create_nitf_tre_structure("TreMTIMSA",desc,hlp=hlp)

def _summary(self):
    res = six.StringIO()
    print("MTIMSA:", file=res)
    print("Image Segment Index: %d" % (self.image_seg_index), file=res)
    print("Static GeoCoords Flag: %d" % (self.geocoords_static), file=res)
    print("Layer Identifier: %s" % (self.layer_id), file=res)
    print("Camera Set Index: %d" % (self.camera_set_index), file=res)
    print("Camera UUID: %s" % (self.camera_id), file=res)
    print("Time Interal Index: %d" % (self.time_interval_index), file=res)
    print("Temporal Block Index: %d" % (self.temp_block_index), file=res)
    print("Nominal Frame Rate: %f" % (self.nominal_frame_rate), file=res)
    print("Absolute Frame Number: %d" % (self.reference_frame_num), file=res)
    print("Base Timestamp: %s" % (self.base_timestamp), file=res)
    print("Frame Delta Time: %d" %  (self.dt_multiplier), file=res)
    print("Size of DT Values: %d" % (self.dt_size), file=res)
    print("Number of Frames: %d" % (self.number_frames), file=res)
    print("Number of Delta_TIME Values: %d" % (self.number_dt), file=res)
    for i in range(self.number_dt):
        print("Number of Delta Time Units: %d" % (self.dt[i]), file=res)

    return res.getvalue()

TreMTIMSA.summary = _summary

__all__ = [ "TreMTIMSA" ]
