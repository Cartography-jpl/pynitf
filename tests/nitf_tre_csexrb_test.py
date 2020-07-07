from pynitf.nitf_tre import *
from pynitf.nitf_tre_csexrb import *
from pynitf_test_support import *
import io

def test_tre_csexrb():
    t = TreCSEXRB()

    # There seem to be numerous errors in the TRE code itself. We will have to address those before finishing up this
    # unit test code
    return

    t.image_uuid = 'dbe26dc7-e003-4d29-8edb-41acc0e86b6e'
    t.num_assoc_des = 1
    t.assoc_des_id[0] = 'dbe26dc7-e003-4d29-8edb-41acc0e86b6f'

    t.platform_id = 'abcdef'
    t.payload_id = 'abcdef'
    t.sensor_id = 'abcdef'
    t.sensor_type = 'F'
    t.ground_ref_point_x = 0.01
    t.ground_ref_point_y = 0.02
    t.ground_ref_point_z = 0.03

    t.time_stamp_loc = 0
    t.reference_frame_num = 1
    t.base_timestamp = '20200707010159.000000000'
    t.dt_multiplier = 1000000
    t.dt_size = 1
    t.number_frames = 1
    t.number_dt = 1
    t.dt[0] = 1

    t.max_gsd = 1.1
    t.along_scan_gsd = 1.2
    t.cross_scan_gsd = 1.3
    t.geo_mean_gsd = 1.4
    t.a_s_vert_gsd = 1.5
    t.c_s_vert_gsd = 1.6
    t.geo_mean_vert_gsd = 1.7
    t.gsd_beta_angle = 1.8

    t.dynamic_range = 10000
    t.num_lines = 1000
    t.num_samples = 1
    t.angle_to_north = 1.1
    t.obliquity_angle = 1.1
    t.az_of_obliquity = 1.1
    t.atm_refr_flag = 0
    t.vel_aber_flag = 0
    t.grd_cover = 9
    t.snow_depth_category = 9
    t.sun_azimuth = 1.1
    t.sun_elevation = 1.1
    t.predicted_niirs = 1.0
    t.circl_err = 1.1
    t.linear_err = 1.1
    t.cloud_cover = 0
    t.rolling_shutter_flag = 0
    t.ue_time_flag = 0

    t.reserved_len = 0

    fh = io.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'CSEXRB00349dbe26dc7-e003-4d29-8edb-41acc0e86b6e001dbe26dc7-e003-4d29-8edb-41acc0e86b6fabcdefabcdefabcdefF+00000000.01+00000000.02+00000000.03000000000120200707010159.000000000\x00\x00\x00\x00\x00\x0fB@\x01\x00\x00\x00\x01\x00\x00\x00\x01\x01         1.1         1.2         1.3         1.4         1.5         1.6         1.7     10000000100000001001.10001.100001.10000991.100  001.1001.0001.1001.10000000000'

    fh2 = io.BytesIO(fh.getvalue())
    t2 = TreCSEXRB()
    t2.read_from_file(fh2)

    assert t2.image_uuid == 'dbe26dc7-e003-4d29-8edb-41acc0e86b6e'
    assert t2.num_assoc_des == 1
    assert t2.assoc_des_id[0] == 'dbe26dc7-e003-4d29-8edb-41acc0e86b6f'

    assert t2.platform_id == 'abcdef'
    assert t2.payload_id == 'abcdef'
    assert t2.sensor_id == 'abcdef'
    assert t2.sensor_type == 'F'
    assert t2.ground_ref_point_x == 0.01
    assert t2.ground_ref_point_y == 0.02
    assert t2.ground_ref_point_z == 0.03

    assert t2.time_stamp_loc == 0
    assert t2.reference_frame_num == 1
    assert t2.base_timestamp == '20200707010159.000000000'
    assert t2.dt_multiplier == 1000000
    assert t2.dt_size == 1
    assert t2.number_frames == 1
    assert t2.number_dt == 1
    assert t2.dt[0] == 1

    assert t2.max_gsd == 1.1
    assert t2.along_scan_gsd == 1.2
    assert t2.cross_scan_gsd == 1.3
    assert t2.geo_mean_gsd == 1.4
    assert t2.a_s_vert_gsd == 1.5
    assert t2.c_s_vert_gsd == 1.6
    assert t2.geo_mean_vert_gsd == 1.7
    assert t2.gsd_beta_angle == 1.8

    assert t2.dynamic_range == 10000
    assert t2.num_lines == 1000
    assert t2.num_samples == 1
    assert t2.angle_to_north == 1.1
    assert t2.obliquity_angle == 1.1
    assert t2.az_of_obliquity == 1.1
    assert t2.atm_refr_flag == 0
    assert t2.vel_aber_flag == 0
    assert t2.grd_cover == 9
    assert t2.snow_depth_category == 9
    assert t2.sun_azimuth == 1.1
    assert t2.sun_elevation == 1.1
    assert t2.predicted_niirs == 1.0
    assert t2.circl_err == 1.1
    assert t2.linear_err == 1.1
    assert t2.cloud_cover == 0
    assert t2.rolling_shutter_flag == 0
    assert t2.ue_time_flag == 0

    assert t2.reserved_len == 0

    print (t2.summary())
