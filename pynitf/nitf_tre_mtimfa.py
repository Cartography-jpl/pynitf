from .nitf_tre import Tre, tre_tag_to_cls
import io

hlp = '''This is the MTIMFA TRE, Motion Imagery File

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (NGA.STND.0044_1.3_MIE4NITF Adjudicated v3.pdf), 
available at https://nsgreg.nga.mil/doc/view?i=4754

MTIMFA is documented in Table 15.
'''
desc = [["layer_id", "Layer Identifier", 36, str],
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

class TreMTIMFA(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "MTIMFA"

tre_tag_to_cls.add_cls(TreMTIMFA)    

__all__ = [ "TreMTIMFA" ]
