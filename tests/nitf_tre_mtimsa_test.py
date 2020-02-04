from pynitf.nitf_tre import *
from pynitf.nitf_tre_mtimsa import *
from pynitf_test_support import *
import io
import struct

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

    fh = io.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'MTIMSA0016004299Some Layer                          043Camera A                            00001704433.3300000000000000045today                   \x00\x00\x00\x00\x00\x00\x04\xd2\x04\x00\x00\x00d\x00\x00\x00\x02\x00\x00\x00{\x00\x00\x00|'

    fh2 = io.BytesIO(fh.getvalue())
    t2 = TreMTIMSA()
    t2.read_from_file(fh2)

    assert t2.image_seg_index == 42
    assert t2.geocoords_static == 99
    assert t2.layer_id == "Some Layer"
    assert t2.camera_set_index == 43
    assert t2.camera_id == "Camera A"
    assert t2.time_interval_index == 17
    assert t2.temp_block_index == 44
    assert t2.nominal_frame_rate == 33.33
    assert t2.reference_frame_num == 45
    assert t2.base_timestamp == "today"
    assert t2.dt_multiplier == 1234
    assert t2.dt_size == 4
    assert t2.number_frames == 100
    assert t2.number_dt == 2
    assert t2.dt[0] == 123
    assert t2.dt[1] == 124

def test_tre_mtimsa_size_2():

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
    t.dt_size = 2
    t.number_frames = 100
    t.number_dt = 2
    print("***** type(dt)", type(t.dt))
    t.dt[0] = 123
    t.dt[1] = 124

    print (t.summary())

    fh = io.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'MTIMSA0015604299Some Layer                          043Camera A                            00001704433.3300000000000000045today                   \x00\x00\x00\x00\x00\x00\x04\xd2\x02\x00\x00\x00d\x00\x00\x00\x02\x00{\x00|'

    fh2 = io.BytesIO(fh.getvalue())
    t2 = TreMTIMSA()
    t2.read_from_file(fh2)

    assert t2.image_seg_index == 42
    assert t2.geocoords_static == 99
    assert t2.layer_id == "Some Layer"
    assert t2.camera_set_index == 43
    assert t2.camera_id == "Camera A"
    assert t2.time_interval_index == 17
    assert t2.temp_block_index == 44
    assert t2.nominal_frame_rate == 33.33
    assert t2.reference_frame_num == 45
    assert t2.base_timestamp == "today"
    assert t2.dt_multiplier == 1234
    assert t2.dt_size == 2
    assert t2.number_frames == 100
    assert t2.number_dt == 2
    assert t2.dt[0] == 123
    assert t2.dt[1] == 124
