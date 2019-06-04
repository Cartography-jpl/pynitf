from pynitf.nitf_tre import *
from pynitf.nitf_tre_mtimfa import *
from pynitf_test_support import *
import io, six
    
def test_tre_mtimfa_basic():

    t = TreMTIMFA()

    #Set some values
    t.layer_id = "Some Layer"
    t.camera_set_index = 42
    t.time_interval_index = 17
    t.num_cameras_defined = 2

    t.camera_id[0] = "Camera A"
    t.num_temp_blocks[0] = 2
    t.start_timestamp[0, 0] = "today"
    t.end_timestamp[0, 0] = "tomorrow"
    t.image_seg_index[0, 0] = 314
    t.start_timestamp[0, 1] = "now"
    t.end_timestamp[0, 1] = "later"
    t.image_seg_index[0, 1] = 159

    t.camera_id[1] = "Camera B"
    t.num_temp_blocks[1] = 1
    t.start_timestamp[1, 0] = "hoy"
    t.end_timestamp[1, 0] = "manana"
    t.image_seg_index[1, 0] = 123

    print (t.summary())

    fh = six.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'MTIMFA00279Some Layer                          042000017002Camera A                            002today                   tomorrow                314now                     later                   159Camera B                            001hoy                     manana                  123'
