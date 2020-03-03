from .nitf_tre import Tre, tre_tag_to_cls
import io

hlp = '''This is the CAMSDA TRE, Camera Set Definition

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (NGA.STND.0044_1.3_MIE4NITF Adjudicated v3.pdf), 
available at https://nsgreg.nga.mil/doc/view?i=4754

CAMSDA is documented in Table 12.
'''
desc = [["num_camera_sets", "Number of Camera Sets", 3, int],
        ["num_camera_sets_in_tre", "Number of Camera Sets in TRE", 3, int],
        ["first_camera_set_in_tre", "First Camera Set in TRE", 3, int],
        [["loop", "f.num_camera_sets_in_tre"],
         ["num_cameras_in_set", "Number of Cameras", 3, int],
         [["loop", "f.num_cameras_in_set[i1]"],
          ["camera_id", "Camera ID", 36, str],
          ["camera_desc", "Camera Description", 80, str],
          ["layer_id", "Layer ID", 36, str],
          ["idlvl", "Image Display Level", 3, int],
          ["ialvl", "Image Attachment Level", 3, int],
          ["iloc", "Image Location", 10, str, {'default' : '0000000000'}],
          ["nrows", "Number of Pixel Rows", 8, int],
          ["ncols", "Number of Pixel Columns", 8, int],
          ],
         ],
]

class TreCAMSDA(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "CAMSDA"

tre_tag_to_cls.add_cls(TreCAMSDA)    

__all__ = [ "TreCAMSDA" ]
