from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the SENSRB TRE, Sensor parameters.

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (STDI-0002 V4.0, available at
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for
where in the document a particular TRE is defined.

SENSRB is documented at Z-13.
'''

_6a_format = "%011.2lf"
_6b_format = "%012.2lf"
_6c_format = "%011.2lf"
_6d_format = "%08.3lf"
_6e_format = "%08.3lf"
_6f_format = "%08.3lf"
_9a_format = _9b_format = _9c_format = _9d_format = "%010.7lf"
_10a_format = _10b_format = _10c_format = "%09.2lf"
# No idea why, but there is both a section 9a and a time stamp 9a which are
# different. This second set is the time stamp
_ts_9a_format = _ts_9b_format = _ts_9c_format = _ts_9d_format = "%010.5f"
desc = ["SENSRB",
        #1. General Data
        ["general_data", "General Data", 1, str, {"default" : "N"}],
        ["sensor", "Sensor Name", 25, str, {'condition' : "f.general_data == 'Y'"}],
        ["sensor_uri", "Sensor URI", 32, str, {'condition' : "f.general_data == 'Y'"}],
        ["platform", "Platform Common Name", 25, str, {'condition' : "f.general_data == 'Y'"}],
        ["platform_uri", "Platform URI", 32, str, {'condition' : "f.general_data == 'Y'"}],
        ["operation_domain", "Operation Domain", 10, str, {'condition' : "f.general_data == 'Y'"}],
        ["content_level", "Content Level", 1, int, {'condition' : "f.general_data == 'Y'"}],
        ["geodetic_system", "Geodetic System", 5, str, {'condition' : "f.general_data == 'Y'"}],
        ["geodetic_type", "Geodetic Type", 1, str, {'condition' : "f.general_data == 'Y'"}],
        ["elevation_datum", "Elevation Datum", 3, str, {'condition' : "f.general_data == 'Y'"}],
        ["length_unit", "Length Unit", 2, str, {'condition' : "f.general_data == 'Y'"}],
        ["angular_unit", "Angular Unit", 3, str, {'condition' : "f.general_data == 'Y'"}],
        ["start_date", "Start Date", 8, int, {'condition' : "f.general_data == 'Y'"}],
        ["start_time", "Start Time", 14, float, {'condition' : "f.general_data == 'Y'", "frmt" : "%014.8f"}],
        ["end_date", "End Date", 8, int, {'condition' : "f.general_data == 'Y'"}],
        ["end_time", "End Time", 14, float, {'condition' : "f.general_data == 'Y'", "frmt" : "%014.8f"}],
        ["generation_count", "Generation Count", 2, int, {'condition' : "f.general_data == 'Y'"}],
        ["generation_date", "Generation Date", 8, int, {'condition' : "f.general_data == 'Y'"}],
        ["generation_time", "Generation Time", 10, float, {'condition' : "f.general_data == 'Y'", "frmt" : "%010.3f"}],
        #2. Sensor Array Data
        ["sensor_array_data", "Sensor Array Data", 1, str, {'default' : 'N'}],
        ["detection", "Detection", 20, str, {'condition' : "f.sensor_array_data == 'Y'"}],
        ["row_detectors", "Row Detectors", 8, int, {'condition' : "f.sensor_array_data == 'Y'", "frmt" : "%08d"}],
        ["column_detectors", "Column Detectors", 8, int, {'condition' : "f.sensor_array_data == 'Y'", "frmt" : "%08d"}],
        ["row_metric", "Row Metric", 8, float, {'condition' : "f.sensor_array_data == 'Y'", "frmt" : "%08.3lf"}],
        ["column_metric", "Column Metric", 8, float, {'condition' : "f.sensor_array_data == 'Y'", "frmt" : "%08.3lf"}],
        ["focal_length", "Focal Length", 8, float, {'condition' : "f.sensor_array_data == 'Y'", "frmt" : "%08.3lf"}],
        ["row_fov", "Row Field of View", 8, float, {'condition' : "f.sensor_array_data == 'Y'", "frmt" : "%08.3lf"}],
        ["column_fov", "Column Field of View", 8, float, {'condition' : "f.sensor_array_data == 'Y'", "frmt" : "%08.3lf"}],
        ["calibrated", "Calibrated", 1, str, {'condition' : "f.sensor_array_data == 'Y'"}],
        #3 Sensor Calibration Data
        ["sensor_calibration_data", "Sensor Calibration Data", 1, str, {'default' : "N"}],
        ["calibration_unit", "Calibration Unit System", 2, str, {'condition' : "f.sensor_calibration_data == 'Y'"}],
        ["principal_point_offset_x", "Principal Point Offset X", 9, float, {'condition' : "f.sensor_calibration_data == 'Y'", "frmt" : "%09lf"}],
        ["principal_point_offset_y", "Principal Point Offset Y", 9, float, {'condition' : "f.sensor_calibration_data == 'Y'", "frmt" : "%09lf"}],
        ["radial_distort_1", "Radial Distortion Coeff 1", 12, str, {'condition' : "f.sensor_calibration_data == 'Y'"}],
        ["radial_distort_2", "Radial Distortion Coeff 2", 12, str, {'condition' : "f.sensor_calibration_data == 'Y'"}],
        ["radial_distort_3", "Radial Distortion Coeff 3", 12, str, {'condition' : "f.sensor_calibration_data == 'Y'"}],
        ["radial_distort_limit", "Radial Distortion Fit Limit", 9, str, {'condition' : "f.sensor_calibration_data == 'Y'"}],
        ["decent_distort_1", "Decentering Distortion Coeff 1", 12, str, {'condition' : "f.sensor_calibration_data == 'Y'"}],
        ["decent_distort_2", "Decentering Distortion Coeff 2", 12, str, {'condition' : "f.sensor_calibration_data == 'Y'"}],
        ["affinity_distort_1", "Affinity Distortion Coeff 1", 12, str, {'condition' : "f.sensor_calibration_data == 'Y'"}],
        ["affinity_distort_2", "Affinity Distortion Coeff 2", 12, str, {'condition' : "f.sensor_calibration_data == 'Y'"}],
        ["calibration_date", "Calibration Date", 8, int, {'condition' : "f.sensor_calibration_data == 'Y'"}],
        #4 Image Formation Data
        ["image_formation_data", "Image Formation Data", 1, str, {"default" : "N"}],
        ["method", "Imaging Method", 15, str, {'condition' : "f.image_formation_data == 'Y'"}],
        ["mode", "Imaging Mode", 3, str, {'condition' : "f.image_formation_data == 'Y'"}],
        ["row_count", "Row Count", 8, int, {'condition' : "f.image_formation_data == 'Y'"}],
        ["column_count", "Column Count", 8, int, {'condition' : "f.image_formation_data == 'Y'"}],
        ["row_set", "Row Detection Set", 8, int, {'condition' : "f.image_formation_data == 'Y'"}],
        ["column_set", "Column Detection Set", 8, int, {'condition' : "f.image_formation_data == 'Y'"}],
        ["row_rate", "Row Detection Rate", 10, int, {'condition' : "f.image_formation_data == 'Y'"}],
        ["column_rate", "Column Detection Rate", 10, int, {'condition' : "f.image_formation_data == 'Y'"}],
        ["first_pixel_row", "First Collected Pixel Row", 8, int, {'condition' : "f.image_formation_data == 'Y'"}],
        ["first_pixel_column", "First Collected Pixel Column", 8, int, {'condition' : "f.image_formation_data == 'Y'"}],
        ["transform_params", "Image Transform Parameter Count", 1, int, {'condition' : "f.image_formation_data == 'Y'"}],
        ["transform_param_1", "Image Transform Parameter 1", 12, str, {'condition' : "f.image_formation_data == 'Y' and f.transform_params >= 1"}],
        ["transform_param_2", "Image Transform Parameter 2", 12, str, {'condition' : "f.image_formation_data == 'Y' and f.transform_params >= 2"}],
        ["transform_param_3", "Image Transform Parameter 3", 12, str, {'condition' : "f.image_formation_data == 'Y' and f.transform_params >= 3"}],
        ["transform_param_4", "Image Transform Parameter 4", 12, str, {'condition' : "f.image_formation_data == 'Y' and f.transform_params >= 4"}],
        ["transform_param_5", "Image Transform Parameter 5", 12, str, {'condition' : "f.image_formation_data == 'Y' and f.transform_params >= 5"}],
        ["transform_param_6", "Image Transform Parameter 6", 12, str, {'condition' : "f.image_formation_data == 'Y' and f.transform_params >= 6"}],
        ["transform_param_7", "Image Transform Parameter 7", 12, str, {'condition' : "f.image_formation_data == 'Y' and f.transform_params >= 7"}],
        ["transform_param_8", "Image Transform Parameter 8", 12, str, {'condition' : "f.image_formation_data == 'Y' and f.transform_params >= 8"}],
        #5. Reference Time / Pixel
        ["reference_time", "Reference Time", 12, float, {"frmt" : "%012.6lf"}],
        ["reference_row", "Reference Pixel Row", 8, float, {"frmt" : "%08.3lf"}],
        ["reference_column", "Reference Pixel Column", 8, float, {"frmt" : "%08.3lf"}],
        #6. Sensor Position Data
        ["latitude_or_x", "Latitude or X", 11, float, {"frmt" : _6a_format}],
        ["longitude_or_y", "Longitude or Y", 12, float, {"frmt" : _6b_format}],
        ["altitude_or_z", "Altitude or Z", 11, float, {"frmt" : _6c_format}],
        ["sensor_x_offset", "Sensor X Position Offset", 8, float, {"frmt" : _6d_format}],
        ["sensor_y_offset", "Sensor Y Position Offset", 8, float, {"frmt" : _6e_format}],
        ["sensor_z_offset", "Sensor Z Position Offset", 8, float, {"frmt" : _6f_format}],
        #7. Attitude Euler Angles
        ["attitude_euler_angles", "Attitude Euler Angles", 1, str, {"default" : "N"}],
        ["sensor_angle_model", "Sensor Angle Model", 1, int, {'condition' : "f.attitude_euler_angles == 'Y'"}],
        ["sensor_angle_1", "Sensor Angle 1", 10, int, {'condition' : "f.attitude_euler_angles == 'Y'"}],
        ["sensor_angle_2", "Sensor Angle 2", 9, int, {'condition' : "f.attitude_euler_angles == 'Y'"}],
        ["sensor_angle_3", "Sensor Angle 3", 10, int, {'condition' : "f.attitude_euler_angles == 'Y'"}],
        ["platform_relative", "Platform Relative Angles", 1, str, {'condition' : "f.attitude_euler_angles == 'Y'"}],
        ["platform_heading", "Platform Heading", 9, int, {'condition' : "f.attitude_euler_angles == 'Y'"}],
        ["platform_pitch", "Platform Pitch", 9, int, {'condition' : "f.attitude_euler_angles == 'Y'"}],
        ["platform_roll", "Platform Roll", 10, int, {'condition' : "f.attitude_euler_angles == 'Y'"}],
        #8. Attitude Unit Vectors
        ["attitude_unit_vectors", "Attitude Unit Vectors", 1, str, {"default" : "N"}],
        ["icx_north_or_x", "Image Coord X Unit Vector 1", 10, int, {'condition' : "f.attitude_unit_vectors == 'Y'"}],
        ["icx_east_or_y", "Image Coord X Unit Vector 2", 10, int, {'condition' : "f.attitude_unit_vectors == 'Y'"}],
        ["icx_down_or_z", "Image Coord X Unit Vector 3", 10, int, {'condition' : "f.attitude_unit_vectors == 'Y'"}],
        ["icy_north_or_x", "Image Coord Y Unit Vector 1", 10, int, {'condition' : "f.attitude_unit_vectors == 'Y'"}],
        ["icy_east_or_y", "Image Coord Y Unit Vector 2", 10, int, {'condition' : "f.attitude_unit_vectors == 'Y'"}],
        ["icy_down_or_z", "Image Coord Y Unit Vector 3", 10, int, {'condition' : "f.attitude_unit_vectors == 'Y'"}],
        ["icz_north_or_x", "Image Coord Z Unit Vector 1", 10, int, {'condition' : "f.attitude_unit_vectors == 'Y'"}],
        ["icz_east_or_y", "Image Coord Z Unit Vector 2", 10, int, {'condition' : "f.attitude_unit_vectors == 'Y'"}],
        ["icz_down_or_z", "Image Coord Z Unit Vector 3", 10, int, {'condition' : "f.attitude_unit_vectors == 'Y'"}],
        #9. Attitude Quaternion
        ["attitude_quaternion", "Attitude Quaternion", 1, str, {"default" : "N"}],
        ["attitude_q1", "Attitude Quaternion Vector 1", 10, float, {'condition' : "f.attitude_quaternion == 'Y'", "frmt" : _9a_format}],
        ["attitude_q2", "Attitude Quaternion Vector 2", 10, float, {'condition' : "f.attitude_quaternion == 'Y'", "frmt" : _9b_format}],
        ["attitude_q3", "Attitude Quaternion Vector 3", 10, float, {'condition' : "f.attitude_quaternion == 'Y'", "frmt" : _9c_format}],
        ["attitude_q4", "Attitude Scalar Component", 10, float, {'condition' : "f.attitude_quaternion == 'Y'", "frmt" : _9d_format}],
        #10. Sensor Velocity Data
        ["sensor_velocity_data", "Sensor Velocity Data", 1, str, {"default" : "N"}],
        ["velocity_north_or_x", "Sensor North Velocity", 9, float, {'condition' : "f.sensor_velocity_data == 'Y'", "frmt" : _10a_format}],
        ["velocity_east_or_y", "Sensor East Velocity", 9, float, {'condition' : "f.sensor_velocity_data == 'Y'", "frmt" : _10b_format}],
        ["velocity_down_or_z", "Sensor Down Velocity", 9, float, {'condition' : "f.sensor_velocity_data == 'Y'", "frmt" : _10c_format}],
        #11. Point Set Data
        ["point_set_data", "Point Set Data", 2, int],
        [["loop", "f.point_set_data"],
         ["point_set_type", "Point Set Type", 25, str],
         ["point_count", "Point Count", 3, int],
         [["loop", "f.point_count[i1]"],
          ["p_row", "Point Row Location", 8, int],
          ["p_column", "Point Column Location", 8, int],
          ["p_latitude", "Point Latitude", 10, int],
          ["p_longitude", "Point Longitude", 11, int],
          ["p_elevation", "Point Elevation", 6, int],
          ["p_range", "Point Range", 8, int],
         ],
        ],
        #12. Time Stamped Data Sets
        ["time_stamped_data_sets", "Time Stamped Data", 2, int],
        [["loop", "f.time_stamped_data_sets"],
         ["time_stamp_type", "Time Stamp Type", 3, str],
         ["time_stamp_count", "Time Stamp Parameter Count", 4, int],
         [["loop", "f.time_stamp_count[i1]"],
          ["time_stamp_time", "Time Stamp Time", 12, float, {"frmt" : "%012.6lf"}],
          ["time_stamp_value_06a", "Time Stamp Value", 11, float, {'condition' : "f.time_stamp_type[i1] == \"06a\"", "frmt": _6a_format}],
          ["time_stamp_value_06b", "Time Stamp Value", 12, float, {'condition' : "f.time_stamp_type[i1] == \"06b\"", "frmt": _6b_format}],
          ["time_stamp_value_06c", "Time Stamp Value", 11, float, {'condition' : "f.time_stamp_type[i1] == \"06c\"", "frmt": _6c_format}],
          ["time_stamp_value_06d", "Time Stamp Value", 8, float, {'condition' : "f.time_stamp_type[i1] == \"06d\"", "frmt": _6d_format}],
          ["time_stamp_value_06e", "Time Stamp Value", 8, float, {'condition' : "f.time_stamp_type[i1] == \"06e\"", "frmt": _6e_format}],
          ["time_stamp_value_06f", "Time Stamp Value", 8, float, {'condition' : "f.time_stamp_type[i1] == \"06f\"", "frmt": _6f_format}],
          ["time_stamp_value_07b", "Time Stamp Value", 10, int, {'condition' : "f.time_stamp_type[i1] == \"07b\""}],
          ["time_stamp_value_07c", "Time Stamp Value", 9, int, {'condition' : "f.time_stamp_type[i1] == \"07c\""}],
          ["time_stamp_value_07d", "Time Stamp Value", 10, int, {'condition' : "f.time_stamp_type[i1] == \"07d\""}],
          ["time_stamp_value_07f", "Time Stamp Value", 9, int, {'condition' : "f.time_stamp_type[i1] == \"07f\""}],
          ["time_stamp_value_07g", "Time Stamp Value", 9, int, {'condition' : "f.time_stamp_type[i1] == \"07g\""}],
          ["time_stamp_value_07h", "Time Stamp Value", 10, int, {'condition' : "f.time_stamp_type[i1] == \"07h\""}],
          ["time_stamp_value_08a", "Time Stamp Value", 10, int, {'condition' : "f.time_stamp_type[i1] == \"08a\""}],
          ["time_stamp_value_08b", "Time Stamp Value", 10, int, {'condition' : "f.time_stamp_type[i1] == \"08b\""}],
          ["time_stamp_value_08c", "Time Stamp Value", 10, int, {'condition' : "f.time_stamp_type[i1] == \"08c\""}],
          ["time_stamp_value_08d", "Time Stamp Value", 10, int, {'condition' : "f.time_stamp_type[i1] == \"08d\""}],
          ["time_stamp_value_08e", "Time Stamp Value", 10, int, {'condition' : "f.time_stamp_type[i1] == \"08e\""}],
          ["time_stamp_value_08f", "Time Stamp Value", 10, int, {'condition' : "f.time_stamp_type[i1] == \"08f\""}],
          ["time_stamp_value_08g", "Time Stamp Value", 10, int, {'condition' : "f.time_stamp_type[i1] == \"08g\""}],
          ["time_stamp_value_08h", "Time Stamp Value", 10, int, {'condition' : "f.time_stamp_type[i1] == \"08h\""}],
          ["time_stamp_value_08i", "Time Stamp Value", 10, int, {'condition' : "f.time_stamp_type[i1] == \"08i\""}],
          ["time_stamp_value_09a", "Time Stamp Value", 10, float, {'condition' : "f.time_stamp_type[i1] == \"09a\"", "frmt": _ts_9a_format}],
          ["time_stamp_value_09b", "Time Stamp Value", 10, float, {'condition' : "f.time_stamp_type[i1] == \"09b\"", "frmt": _ts_9b_format}],
          ["time_stamp_value_09c", "Time Stamp Value", 10, float, {'condition' : "f.time_stamp_type[i1] == \"09c\"", "frmt": _ts_9c_format}],
          ["time_stamp_value_09d", "Time Stamp Value", 10, float, {'condition' : "f.time_stamp_type[i1] == \"09d\"", "frmt": _ts_9d_format}],
          ["time_stamp_value_10a", "Time Stamp Value", 9, int, {'condition' : "f.time_stamp_type[i1] == \"10a\""}],
          ["time_stamp_value_10b", "Time Stamp Value", 9, int, {'condition' : "f.time_stamp_type[i1] == \"10b\""}],
          ["time_stamp_value_10c", "Time Stamp Value", 9, int, {'condition' : "f.time_stamp_type[i1] == \"10c\""}],
         ],
        ],
        #13. Pixel Referenced Data Sets
        #TODO: This code has not been tested
        ["pixel_referenced_data_sets", "Pixel Reference Data", 2, int],
        [["loop", "f.pixel_referenced_data_sets"],
         ["pixel_reference_type", "Pixel Reference Type", 3, str],
         ["pixel_reference_count", "Pixel Reference Parameter Count", 4, int],
         [["loop", "f.pixel_reference_count[i1]"],
          ["pixel_reference_row", "Pixel Reference Row", 8, int],
          ["pixel_reference_column", "Pixel Reference Column", 8, int],
          ["pixel_reference_value", "Pixel Reference Value", 11, int, {'condition' : "f.pixel_reference_type[i1] == \"06a\""}],
          ["pixel_reference_value", "Pixel Reference Value", 12, int, {'condition' : "f.pixel_reference_type[i1] == \"06b\""}],
          ["pixel_reference_value", "Pixel Reference Value", 11, int, {'condition' : "f.pixel_reference_type[i1] == \"06c\""}],
          ["pixel_reference_value", "Pixel Reference Value", 8, int, {'condition' : "f.pixel_reference_type[i1] == \"06d\""}],
          ["pixel_reference_value", "Pixel Reference Value", 8, int, {'condition' : "f.pixel_reference_type[i1] == \"06e\""}],
          ["pixel_reference_value", "Pixel Reference Value", 8, int, {'condition' : "f.pixel_reference_type[i1] == \"06f\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"07b\""}],
          ["pixel_reference_value", "Pixel Reference Value", 9, int, {'condition' : "f.pixel_reference_type[i1] == \"07c\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"07d\""}],
          ["pixel_reference_value", "Pixel Reference Value", 9, int, {'condition' : "f.pixel_reference_type[i1] == \"07f\""}],
          ["pixel_reference_value", "Pixel Reference Value", 9, int, {'condition' : "f.pixel_reference_type[i1] == \"07g\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"07h\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"08a\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"08b\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"08c\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"08d\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"08e\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"08f\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"08g\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"08h\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"08i\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"09a\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"09b\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"09c\""}],
          ["pixel_reference_value", "Pixel Reference Value", 10, int, {'condition' : "f.pixel_reference_type[i1] == \"09d\""}],
          ["pixel_reference_value", "Pixel Reference Value", 9, int, {'condition' : "f.pixel_reference_type[i1] == \"10a\""}],
          ["pixel_reference_value", "Pixel Reference Value", 9, int, {'condition' : "f.pixel_reference_type[i1] == \"10b\""}],
          ["pixel_reference_value", "Pixel Reference Value", 9, int, {'condition' : "f.pixel_reference_type[i1] == \"10c\""}],
         ],
        ],
        #14. Uncertainty Data
        ["uncertainty_data", "Uncertainty Data", 3, int],
        [["loop", "f.uncertainty_data"],
         ["uncertainty_first_type", "Uncertainty First Index", 11, str],
         ["uncertainty_second_type", "Uncertainty Second Index", 11, str],
         ["uncertainty_value", "Uncertainty Value", 10, str],
        ],
        #15. Additional Parameter data
        ["additional_parameter_data", "Additional Parameters", 3, int],
        [["loop", "f.additional_parameter_data"],
         ["parameter_name", "Parameter Name", 25, str],
         ["parameter_size", "Parameter Field Size", 3, int],
         ["parameter_count", "Parameter Value Count", 4, int],
         [["loop", "f.parameter_count[i1]"],
          ["parameter_value", "Parameter value", "f.parameter_size[i1]", None,
           {'field_value_class' : FieldData, 'size_not_updated' : True}]
         ],
        ],
]

TreSENSRB = create_nitf_tre_structure("TreSENSRB",desc,hlp=hlp)

def _summary(self):
    res = six.StringIO()
    print("SENSRB Flags 1:%s 2:%s 3:%s 4:%s ... 7:%s 8:%s 9:%s 10:%s 11:%d 12:%d 13:%d 14:%d 15:%d " % (self.general_data, \
            self.sensor_array_data, self.sensor_calibration_data, self.image_formation_data, \
            self.attitude_euler_angles, self.attitude_unit_vectors, self.attitude_quaternion, \
            self.sensor_velocity_data, self.point_set_data, self.time_stamped_data_sets,\
            self.pixel_referenced_data_sets, self.uncertainty_data, self.additional_parameter_data), file=res)
    return res.getvalue()

TreSENSRB.summary = _summary

__all__ = [ "TreSENSRB" ]
