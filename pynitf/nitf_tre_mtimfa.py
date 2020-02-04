from .nitf_field import *
from .nitf_tre import *
import io

hlp = '''This is the MTIMFA TRE, Motion Imagery File

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (NGA.STND.0044_1.3_MIE4NITF Adjudicated v3.pdf), 
available at https://nsgreg.nga.mil/doc/view?i=4754

MTIMFA is documented in Table 15.
'''
desc = ["MTIMFA",
        ["layer_id", "Layer Identifier", 36, str],
        ["camera_set_index", "Camera Set Index", 3, int],
        ["time_interval_index", "Time Interval Index", 6, int],
        ["num_cameras_defined", "Number of Defined Cameras", 3, int],
        [["loop", "f.num_cameras_defined"],
         ["camera_id", "Camera UUID", 36, str],
         ["num_temp_blocks", "Number of Temporal Blocks", 3, int],
         [["loop", "f.num_temp_blocks[i1]"],
          ["start_timestamp", "Temporal Block Start Time", 24, str],
          ["end_timestamp", "Temporal Block End Time", 24, str],
          ["image_seg_index", "Image Segment Index", 3, int],
          ],
         ],
]

TreMTIMFA = create_nitf_tre_structure("TreMTIMFA",desc,hlp=hlp)

def _summary(self):
    res = io.StringIO()
    print("MTIMFA:", file=res)
    print("Layer Identifier: %s" % (self.layer_id), file=res)
    print("Camera Set Index: %d" % (self.camera_set_index), file=res)
    print("Time Interval Index: %d" % (self.time_interval_index), file=res)
    print("Number of Defined Cameras: %d" % (self.num_cameras_defined), file=res)
    for i in range(self.num_cameras_defined):
        print("Camera UUID: %s" % (self.camera_id[i]), file=res)
        print("Number of Temporal Blocks: %d" % (self.num_temp_blocks[i]), file=res)
        for j in range(self.num_temp_blocks[i]):
            print("Temporal Block Start Time: %s" % (self.start_timestamp[i, j]), file=res)
            print("Temporal Block End Time: %s" % (self.end_timestamp[i, j]), file=res)
            print("Image Segment Index: %d" % (self.image_seg_index[i, j]), file=res)

    return res.getvalue()

TreMTIMFA.summary = _summary

__all__ = [ "TreMTIMFA" ]
