from pynitf.nitf_tre import *
from pynitf.nitf_tre_sensrb import *
from pynitf_test_support import *
import io, six

def turn_everything_off(t):
    '''Initialize everything to off, so we can selectively turn things
    on in a unit test.'''
    t.general_data='N'
    t.sensor_array_data='N'
    t.sensor_calibration_data='N'
    t.image_formation_data='N'
    t.attitude_euler_angles='N'
    t.attitude_unit_vectors='N'
    t.attitude_quaternion='N'
    t.sensor_velocity_data='N'
    t.point_set_data=0
    t.time_stamped_data_sets=0
    t.pixel_referenced_data_sets=0
    t.uncertainty_data=0
    t.additional_parameter_data=0

def fill_in_5_and_6(t):
    '''Section 5 and 6 of tre are always required, so have some default
    values to fill in here'''
    # section 5 stuff is always present
    t.reference_time = 0
    t.reference_row=0
    t.reference_column=0
    # section 6 stuff is always present
    t.latitude_or_x = 10
    t.longitude_or_y = 20
    t.altitude_or_z = 100000
    t.sensor_x_offset=0
    t.sensor_y_offset=0
    t.sensor_z_offset=0

def test_tre_sensrb_empty():
    '''Basic test of sensrb where we have everything turned off, and only
    fill in the always on sections'''
    t = TreSENSRB()
    turn_everything_off(t)
    fill_in_5_and_6(t)
    # Section 5 and 6 always need to be filled in
    fill_in_5_and_6(t)
    fh = six.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'SENSRB00106NNNN00000.0000000000.0000000.00000000010.00000000020.0000100000.000000.0000000.0000000.000NNNN000000000000'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreSENSRB()
    t2.read_from_file(fh2)
    assert t2.reference_time  ==  0
    assert t2.reference_row == 0
    assert t2.reference_column == 0
    assert t2.latitude_or_x  ==  10
    assert t2.longitude_or_y  ==  20
    assert t2.altitude_or_z  ==  100000
    assert t2.sensor_x_offset == 0
    assert t2.sensor_y_offset == 0
    assert t2.sensor_z_offset == 0
    
def test_tre_sensrb_general_data():
    '''Basic test of sensrb, general_data part only'''
    t = TreSENSRB()
    # Turn on general_data, and off everything else
    turn_everything_off(t)
    t.general_data='Y'

    # Set some values
    t.sensor="My sensor"
    t.sensor_uri="blah"
    t.platform="My platform"
    t.platform_uri="blah"
    t.operation_domain="blah"
    t.content_level=1
    t.geodetic_system="WGS84"
    t.geodetic_type="G"
    t.elevation_datum="HAE"
    t.length_unit="SI"
    t.angular_unit="D"
    t.start_date=20170427
    t.start_time=0.99999999
    t.end_date=20170427
    t.end_time=86399.99999999
    t.generation_count=0
    t.generation_date=20170427
    t.generation_time=235959.999
    # Section 5 and 6 always need to be filled in
    fill_in_5_and_6(t)
    fh = six.BytesIO()
    t.write_to_file(fh)
    #print(fh.getvalue())
    assert fh.getvalue() == b'SENSRB00309YMy sensor                blah                            My platform              blah                            blah      1WGS84GHAESID  2017042700000.999999992017042786399.999999990020170427235959.999NNN00000.0000000000.0000000.00000000010.00000000020.0000100000.000000.0000000.0000000.000NNNN000000000000'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreSENSRB()
    t2.read_from_file(fh2)
    assert t2.sensor_array_data == 'N'
    assert t2.sensor_calibration_data == 'N'
    assert t2.image_formation_data == 'N'
    assert t2.attitude_euler_angles == 'N'
    assert t2.attitude_unit_vectors == 'N'
    assert t2.attitude_quaternion == 'N'
    assert t2.sensor_velocity_data == 'N'
    assert t2.point_set_data == 0
    assert t2.time_stamped_data_sets == 0
    assert t2.pixel_referenced_data_sets == 0
    assert t2.uncertainty_data == 0
    assert t2.additional_parameter_data == 0
    assert t2.sensor == "My sensor"
    assert t2.sensor_uri == "blah"
    assert t2.platform == "My platform"
    assert t2.platform_uri == "blah"
    assert t2.operation_domain == "blah"
    assert t2.content_level == 1
    assert t2.geodetic_system == "WGS84"
    assert t2.geodetic_type == "G"
    assert t2.elevation_datum == "HAE"
    assert t2.length_unit == "SI"
    assert t2.angular_unit == "D"
    assert t2.start_date == 20170427
    assert t2.start_time == 0.99999999
    assert t2.end_date == 20170427
    assert t2.end_time == 86399.99999999
    assert t2.generation_count == 0
    assert t2.generation_date == 20170427
    assert t2.generation_time == 235959.999

    print("\n" + t2.summary())

def test_tre_sensrb_additional_parameter():
    t = TreSENSRB()
    # Turn everything off
    turn_everything_off(t)
    # Fill in stuff always needed
    fill_in_5_and_6(t)
    t.additional_parameter_data = 2
    t.parameter_name[0]="parm 1"
    t.parameter_name[1]="parm 2"
    t.parameter_size[0]=1
    t.parameter_size[1]=2
    t.parameter_count[0] = 1
    t.parameter_count[1] = 3
    t.parameter_value[0,0] = b'0'
    t.parameter_value[1,0] = b'00'
    t.parameter_value[1,1] = b'01'
    t.parameter_value[1,2] = b'02'
    fh = six.BytesIO()
    t.write_to_file(fh)
    #print(fh.getvalue())
    assert fh.getvalue() == b'SENSRB00177NNNN00000.0000000000.0000000.00000000010.00000000020.0000100000.000000.0000000.0000000.000NNNN000000000002parm 1                   00100010parm 2                   0020003000102'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreSENSRB()
    t2.read_from_file(fh2)
    assert t2.additional_parameter_data  ==  2
    assert list(t.parameter_name) == ["parm 1", "parm 2"]
    assert list(t.parameter_size) == [1,2]
    assert list(t.parameter_count) == [1,3]
    assert t2.parameter_value[0,0]  ==  b'0'
    assert t2.parameter_value[1,0]  ==  b'00'
    assert t2.parameter_value[1,1]  ==  b'01'
    assert t2.parameter_value[1,2]  ==  b'02'
    
def test_tre_sensrb_sensor_array():
    '''Basic test of sensrb, sensor_array_data part only'''

    t = TreSENSRB()
    # Turn everything off
    turn_everything_off(t)
    # Fill in stuff always needed
    fill_in_5_and_6(t)

    #Fill in sensor array data
    t.sensor_array_data = "Y"
    t.detection = "some detection"
    t.row_detectors = 1000
    t.column_detectors = 1000
    t.row_metric = 1.1
    t.column_metric = 1.1
    t.focal_length = 1.2
    t.row_fov = 1.3
    t.column_fov = 1.3
    t.calibrated = "Y"

    fh = six.BytesIO()
    t.write_to_file(fh)
    #print(fh.getvalue())
    assert fh.getvalue() == b'SENSRB00183NYsome detection      00001000000010000001.1000001.1000001.2000001.3000001.300YNN00000.0000000000.0000000.00000000010.00000000020.0000100000.000000.0000000.0000000.000NNNN000000000000'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreSENSRB()
    t2.read_from_file(fh2)
    assert t2.detection == "some detection"
    assert t2.row_detectors == 1000
    assert t2.column_detectors == 1000
    assert t2.row_metric == 1.1
    assert t2.column_metric == 1.1
    assert t2.focal_length == 1.2
    assert t2.row_fov == 1.3
    assert t2.column_fov == 1.3
    assert t2.calibrated == "Y"

def test_tre_sensrb_sensor_calibration_data():
    '''Basic test of sensrb, sensor_calibration_data part only'''

    t = TreSENSRB()
    # Turn everything off
    turn_everything_off(t)
    # Fill in stuff always needed
    fill_in_5_and_6(t)

    # Fill in sensor calibration data
    t.sensor_calibration_data = "Y"
    t.calibration_unit = "mm"
    t.principal_point_offset_x = +1.0
    t.principal_point_offset_y = -1.0
    t.radial_distort_1 = "1e2"
    t.radial_distort_2 = "2e2"
    t.radial_distort_3 = "3e2"
    t.radial_distort_limit = "+000001.0"
    t.decent_distort_1 = "1e3"
    t.decent_distort_2 = "2.1e2"
    t.affinity_distort_1 = "3.7e5"
    t.affinity_distort_2 = "6.4e2"
    t.calibration_date = 20170505

    fh = six.BytesIO()
    t.write_to_file(fh)
    #print(fh.getvalue())
    assert fh.getvalue() == b'SENSRB00227NNYmm01.000000-1.0000001e2         2e2         3e2         +000001.01e3         2.1e2       3.7e5       6.4e2       20170505N00000.0000000000.0000000.00000000010.00000000020.0000100000.000000.0000000.0000000.000NNNN000000000000'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreSENSRB()
    t2.read_from_file(fh2)
    assert t.sensor_calibration_data == "Y"
    assert t.calibration_unit == "mm"
    assert t.principal_point_offset_x == +1.0
    assert t.principal_point_offset_y == -1.0
    assert t.radial_distort_1 == "1e2"
    assert t.radial_distort_2 == "2e2"
    assert t.radial_distort_3 == "3e2"
    assert t.radial_distort_limit == "+000001.0"
    assert t.decent_distort_1 == "1e3"
    assert t.decent_distort_2 == "2.1e2"
    assert t.affinity_distort_1 == "3.7e5"
    assert t.affinity_distort_2 == "6.4e2"
    assert t.calibration_date == 20170505

def test_tre_sensrb_attitude_quaternion():
    '''Basic test of sensrb, sensor_attitude_quaternion part only'''

    t = TreSENSRB()
    # Turn everything off
    turn_everything_off(t)
    # Fill in stuff always needed
    fill_in_5_and_6(t)

    # Fill in sensor calibration data
    t.attitude_quaternion = "Y"
    t.attitude_q1 = 0.0001
    t.attitude_q2 = 0.0002
    t.attitude_q3 = 0.0003
    t.attitude_q4 = 0.0004

    fh = six.BytesIO()
    t.write_to_file(fh)
    #print(fh.getvalue())
    assert fh.getvalue() == b'SENSRB00146NNNN00000.0000000000.0000000.00000000010.00000000020.0000100000.000000.0000000.0000000.000NNY0000.000100000.000200000.000300000.00040N000000000000'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreSENSRB()
    t2.read_from_file(fh2)
    assert t.attitude_quaternion == "Y"
    assert t.attitude_q1 == 0.0001
    assert t.attitude_q2 == 0.0002
    assert t.attitude_q3 == 0.0003
    assert t.attitude_q4 == 0.0004


def test_tre_sensrb_time_stamped_data_sets():
    #Basic test of sensrb, sensor_calibration_data part only

    positionCount = 5
    attitudeCount = 5

    t = TreSENSRB()
    # Turn everything off
    turn_everything_off(t)
    # Fill in stuff always needed
    fill_in_5_and_6(t)

    # Fill in sensor calibration data

    t.time_stamped_data_sets = 10
    t.time_stamp_type[0] = "06a"
    t.time_stamp_count[0] = positionCount
    for i in range(positionCount):
        t.time_stamp_time[0,i] = 0.98
        t.time_stamp_value_06a[0,i] = 654321.9876
    t.time_stamp_type[1] = "06b"
    t.time_stamp_count[1] = positionCount
    for i in range(positionCount):
        t.time_stamp_time[1, i] = 0.12345
        t.time_stamp_value_06b[1, i] = 7654321.9876
    t.time_stamp_type[2] = "06c"
    t.time_stamp_count[2] = positionCount
    for i in range(positionCount):
        t.time_stamp_time[2, i] = 0.01
        t.time_stamp_value_06c[2, i] = 0.01
    t.time_stamp_type[3] = "06d"
    t.time_stamp_count[3] = positionCount
    for i in range(positionCount):
        t.time_stamp_time[3, i] = 0.01
        t.time_stamp_value_06d[3, i] = 0.01
    t.time_stamp_type[4] = "06e"
    t.time_stamp_count[4] = positionCount
    for i in range(positionCount):
        t.time_stamp_time[4, i] = 0.01
        t.time_stamp_value_06e[4, i] = 0.01
    t.time_stamp_type[5] = "06f"
    t.time_stamp_count[5] = positionCount
    for i in range(positionCount):
        t.time_stamp_time[5, i] = 0.01
        t.time_stamp_value_06f[5, i] = 0.01
    t.time_stamp_type[6] = "09a"
    t.time_stamp_count[6] = attitudeCount
    for i in range(attitudeCount):
        t.time_stamp_time[6, i] = 0.01
        t.time_stamp_value_09a[6, i] = 0.01
    t.time_stamp_type[7] = "09b"
    t.time_stamp_count[7] = attitudeCount
    for i in range(attitudeCount):
        t.time_stamp_time[7, i] = 0.01
        t.time_stamp_value_09b[7, i] = 0.01
    t.time_stamp_type[8] = "09c"
    t.time_stamp_count[8] = attitudeCount
    for i in range(attitudeCount):
        t.time_stamp_time[8, i] = 0.01
        t.time_stamp_value_09c[8, i] = 0.01
    t.time_stamp_type[9] = "09d"
    t.time_stamp_count[9] = attitudeCount
    for i in range(attitudeCount):
        t.time_stamp_time[9, i] = 99999.999999
        t.time_stamp_value_09d[9, i] = 0808.08080
    fh = six.BytesIO()
    t.write_to_file(fh)
    #print(fh.getvalue())
    assert fh.getvalue() == b'SENSRB01266NNNN00000.0000000000.0000000.00000000010.00000000020.0000100000.000000.0000000.0000000.000NNNN001006a000500000.98000000654321.9900000.98000000654321.9900000.98000000654321.9900000.98000000654321.9900000.98000000654321.9906b000500000.123450007654321.9900000.123450007654321.9900000.123450007654321.9900000.123450007654321.9900000.123450007654321.9906c000500000.01000000000000.0100000.01000000000000.0100000.01000000000000.0100000.01000000000000.0100000.01000000000000.0106d000500000.0100000000.01000000.0100000000.01000000.0100000000.01000000.0100000000.01000000.0100000000.01006e000500000.0100000000.01000000.0100000000.01000000.0100000000.01000000.0100000000.01000000.0100000000.01006f000500000.0100000000.01000000.0100000000.01000000.0100000000.01000000.0100000000.01000000.0100000000.01009a000500000.0100000000.0100000000.0100000000.0100000000.0100000000.0100000000.0100000000.0100000000.0100000000.0100009b000500000.0100000000.0100000000.0100000000.0100000000.0100000000.0100000000.0100000000.0100000000.0100000000.0100009c000500000.0100000000.0100000000.0100000000.0100000000.0100000000.0100000000.0100000000.0100000000.0100000000.0100009d000599999.9999990808.0808099999.9999990808.0808099999.9999990808.0808099999.9999990808.0808099999.9999990808.0808000000000'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreSENSRB()
    t2.read_from_file(fh2)
    assert t2.time_stamped_data_sets == 10
    assert t2.time_stamp_type[0] == "06a"
    assert t2.time_stamp_count[0] == positionCount
    for i in range(positionCount):
        assert t2.time_stamp_time[0, i] == 0.98
        assert t2.time_stamp_value_06a[0, i] == 654321.99
    assert t2.time_stamp_type[1] == "06b"
    assert t2.time_stamp_count[1] == positionCount
    for i in range(positionCount):
        assert t2.time_stamp_time[1, i] == 0.12345
        assert t2.time_stamp_value_06b[1, i] == 7654321.99
    assert t2.time_stamp_type[2] == "06c"
    assert t2.time_stamp_count[2] == positionCount
    for i in range(positionCount):
        assert t2.time_stamp_time[2, i] == 0.01
        assert t2.time_stamp_value_06c[2, i] == 0.01
    assert t2.time_stamp_type[3] == "06d"
    assert t2.time_stamp_count[3] == positionCount
    for i in range(positionCount):
        assert t2.time_stamp_time[3, i] == 0.01
        assert t2.time_stamp_value_06d[3, i] == 0.01
    assert t2.time_stamp_type[4] == "06e"
    assert t2.time_stamp_count[4] == positionCount
    for i in range(positionCount):
        assert t2.time_stamp_time[4, i] == 0.01
        assert t2.time_stamp_value_06e[4, i] == 0.01
    assert t2.time_stamp_type[5] == "06f"
    assert t2.time_stamp_count[5] == positionCount
    for i in range(positionCount):
        assert t2.time_stamp_time[5, i] == 0.01
        assert t2.time_stamp_value_06f[5, i] == 0.01
    assert t2.time_stamp_type[6] == "09a"
    assert t2.time_stamp_count[6] == attitudeCount
    for i in range(attitudeCount):
        assert t2.time_stamp_time[6, i] == 0.01
        assert t2.time_stamp_value_09a[6, i] == 0.01
    assert t2.time_stamp_type[7] == "09b"
    assert t2.time_stamp_count[7] == attitudeCount
    for i in range(attitudeCount):
        assert t2.time_stamp_time[7, i] == 0.01
        assert t2.time_stamp_value_09b[7, i] == 0.01
    assert t2.time_stamp_type[8] == "09c"
    assert t2.time_stamp_count[8] == attitudeCount
    for i in range(attitudeCount):
        assert t2.time_stamp_time[8, i] == 0.01
        assert t2.time_stamp_value_09c[8, i] == 0.01
    assert t2.time_stamp_type[9] == "09d"
    assert t2.time_stamp_count[9] == attitudeCount
    for i in range(attitudeCount):
        assert t2.time_stamp_time[9, i] == 99999.999999
        assert t2.time_stamp_value_09d[9, i] == 0808.08080

# Tests for other parts
