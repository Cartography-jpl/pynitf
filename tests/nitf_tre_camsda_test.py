from pynitf.nitf_tre import *
from pynitf.nitf_tre_camsda import *
from pynitf_test_support import *
import io
    
def test_tre_camsda_basic():

    t = TreCAMSDA()

    #Set some values
    t.num_camera_sets = 42
    t.num_camera_sets_in_tre = 2
    t.first_camera_set_in_tre = 1

    t.num_cameras_in_set[0] = 1

    t.camera_id[0, 0] = "CAM_0_0"
    t.camera_desc[0, 0] = "HD camera in first camera set"
    t.layer_id[0, 0] = "Cam 0 0 layer"
    t.idlvl[0, 0] = 42
    t.ialvl[0, 0] = 12
    t.iloc[0, 0] = 123456789
    t.nrows[0, 0] = 1080
    t.ncols[0, 0] = 1920

    t.num_cameras_in_set[1] = 2

    t.camera_id[1, 0] = "CAM_1_0"
    t.camera_desc[1, 0] = "VGA camera in second camera set"
    t.layer_id[1, 0] = "Cam 1 0 layer"
    t.idlvl[1, 0] = 43
    t.ialvl[1, 0] = 13
    t.iloc[1, 0] = 67891234
    t.nrows[1, 0] = 480
    t.ncols[1, 0] = 640

    t.camera_id[1, 1] = "CAM_1_1"
    t.camera_desc[1, 1] = "Super VGA camera in second camera set"
    t.layer_id[1, 1] = "Cam 1 1 layer"
    t.idlvl[1, 1] = 44
    t.ialvl[1, 1] = 14
    t.iloc[1, 1] = 5432167
    t.nrows[1, 1] = 600
    t.ncols[1, 1] = 800

    print (t.summary())

    fh = io.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'CAMSDA00567042002001001CAM_0_0                             HD camera in first camera set                                                   Cam 0 0 layer                       042012123456789 0000108000001920002CAM_1_0                             VGA camera in second camera set                                                 Cam 1 0 layer                       04301367891234  0000048000000640CAM_1_1                             Super VGA camera in second camera set                                           Cam 1 1 layer                       0440145432167   0000060000000800'
    
