from pynitf.nitf_tre import *
from pynitf.nitf_tre_mtimsa import *
from pynitf_test_support import *
import io, six
    
def test_tre_mtimsa_basic():

    t = TreMTIMSA()

    #Set some values
    t.image_seg_index = 42
    t.geocoords_static = 99
    t.layer_id = "Some Layer"
    t.camera_set_index = 43
    t.camera_id = "Camera A"
    t.time_interval_index = 17
    t.temp_block_index = 44
    t.nominal_frame_rate = 33.33
    t.reference_frame_num = 45
    t.base_timestamp = "today"
    t.dt_multiplier = 1234
    t.dt_size = 4
    t.number_frames = 100
    t.number_dt = 2
    print("***** type(dt)", type(t.dt))
    t.dt[0] = 123
    t.dt[1] = 124

    print (t.summary())

    fh = six.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'MTIMSA0016004299Some Layer                          043Camera A                            00001704433.33        000000045today                   00001234401000002\x00\x00\x00{\x00\x00\x00|'
