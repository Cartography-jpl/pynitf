from .nitf_field import *
from .nitf_tre import *
import io

hlp = '''This is the CAMSDA TRE, Camera Set Definition

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (NGA.STND.0044_1.3_MIE4NITF Adjudicated v3.pdf), 
available at https://nsgreg.nga.mil/doc/view?i=4754

CAMSDA is documented in Table 12.
'''
desc = ["CAMSDA",
        ["num_camera_sets", "Number of Camera Sets", 3, int],
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

TreCAMSDA = create_nitf_tre_structure("TreCAMSDA",desc,hlp=hlp)

def _summary(self):
    res = io.StringIO()
    print("CAMSDA:", file=res)
    print("Number of Camera Sets: %d" % (self.num_camera_sets), file=res)
    print("Number of Camera Sets in TRE: %d" % (self.num_camera_sets_in_tre), file=res)
    for i in range(self.num_camera_sets_in_tre):
        print("Camera Set %d:" % (i), file=res)
        print("Number of Cameras in Set: %d" % (self.num_cameras_in_set[i]), file=res)
        for j in range(self.num_cameras_in_set[i]):
            print("Camera ID: %s" % (self.camera_id[i, j]), file=res)
            print("Camera Description: %s" % (self.camera_desc[i, j]), file=res)
            print("Layer ID: %s" % (self.layer_id[i, j]), file=res)
            print("Image Display Level: %d" % (self.idlvl[i, j]), file=res)
            print("Image Attachment Level: %d" % (self.ialvl[i, j]), file=res)
            print("Image Location: %s" % (self.iloc[i, j]), file=res)
            print("Number of Pixel Rows: %d" % (self.nrows[i, j]), file=res)
            print("Number of Pixel Columns: %d" % (self.ncols[i, j]), file=res)

    return res.getvalue()

TreCAMSDA.summary = _summary

__all__ = [ "TreCAMSDA" ]
