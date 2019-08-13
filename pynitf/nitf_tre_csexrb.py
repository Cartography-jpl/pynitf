from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the CSEXRB TRE. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation.

This particular TRE is not officially adopted yet, it is part of the new
GLAS/GFM standard in the SNIP. The TRE is documented in "10c GLAS-GFM 
Supporting TREs Combined V2"

'''

_pt_format = "%+012.2lf"
_tm_format = "%+016.9lf"
_gsd_format = "%12.1lf"

desc = ["CSEXRB",

        ["image_uuid", "UUID Assigned to Current Image Plane", 36, str],
        ["num_assoc_des", "Number of Associated DES", 3, int],
        [["loop", "f.num_assoc_des"],
         ["assoc_des_id", "UUID of DES Associated with this Image", 36, str],
        ],
        ["platform_id", "Platform Identifier", 6, str],
        ["payload_id", "Payload Identifier", 6, str],
        ["sensor_id", "Sensor Identifier", 6, str],
        ["sensor_type", "Sensor Type", 1, str],
        ["ground_ref_point_x", "X coordinate of Ground reference point", 12,
         float, {"frmt" : _pt_format}],
        ["ground_ref_point_y", "Y coordinate of Ground reference point", 12,
         float, {"frmt" : _pt_format}],
        ["ground_ref_point_z", "Z coordinate of Ground reference point", 12,
         float, {"frmt" : _pt_format}],
        ["day_first_line_image", "Day of First Line of Synthetic Array Image",
         8, str, {'condition': 'f.sensor_type=="S"'}],
        ["time_first_line_image", "Time of First Line of Synthetic Array Image",
         15, str, {'condition': 'f.sensor_type=="S"'}],
        ["time_image_duration", "Time of Image Duration",
         16, float, {'condition': 'f.sensor_type=="S"', "frmt" : _tm_format}],
        ["time_stamp_loc", "Location of Frame Time Stamps", 1, int,
         {'condition': 'f.sensor_type=="F"'}],
        ["reference_frame_num", "Reference Frame Identifier", 9, int,
         {'condition': 'f.sensor_type=="F" and f.time_stamp_loc==0'}],
        ["base_timestamp", "Base Timestamp", 24, str,
         {'condition': 'f.sensor_type=="F" and f.time_stamp_loc==0'}],
         ["dt_multiplier", "Delta Time Duration", 8, None,
         {'condition': 'f.sensor_type=="F" and f.time_stamp_loc==0',
          'field_value_class' : IntFieldData, 'size_not_updated' : True}],
        ["dt_size", "Byte Size of the Delta Time Values", 1, bytes,
         {'condition': 'f.sensor_type=="F" and f.time_stamp_loc==0'}],
        ["number_frames", "Byte Size of the Delta Time Values", 4, None,
         {'condition': 'f.sensor_type=="F" and f.time_stamp_loc==0',
          'field_value_class' : IntFieldData, 'size_not_updated' : True}],
        ["number_dt", "Number of Delta Time Values", 4, None,
         {'condition': 'f.sensor_type=="F" and f.time_stamp_loc==0',
          'field_value_class' : IntFieldData, 'size_not_updated' : True}],
        [["loop", "f.number_dt", {'condition': 'f.sensor_type=="F" and f.time_stamp_loc==0'}],
         ["dt", "Delta Time Values", "f.dt_size", None,
          { 'field_value_class' : IntFieldData, 'size_not_updated' : True}],
        ],
        ["max_gsd", "Maximum Mean Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_format, "optional" : True}],
        ["along_scan_gsd", "Measured Along-Scan Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_format, "optional" : True}],
        ["cross_scan_gsd", "Measured Cross-Scan Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_format, "optional" : True}],
        ["geo_scan_gsd", "Measured Geometric Mean Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_format, "optional" : True}],
        ["a_s_vert_gsd", "Measured Along-Scan Vertical Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_format, "optional" : True}],
        ["c_s_vert_gsd", "Measured Cross-Scan Vertical Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_format, "optional" : True}],
        ["geo_mean_vert_gsd", "Measured Geometric Mean Vertical Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_format, "optional" : True}],
        ["geo_beta_angle", "Angle Between Along-Scan and Cross-Scan Directions",
         5, float, {"frmt" : _gsd_format, "optional" : True}],
        ["dynamic_range", "Dynamic Range of Pixels in Image Across All Bands",
         5, int, {"optional" : True}],
        ["num_lines", "Number of Lines in the Entire Image Plane",
         7, int],
        ["num_samples", "Number of Samples in the Entire Image Plane",
         5, int],
        ["angle_to_north", "Nominal Angle to True North", 7, float,
         {'frmt' : '%07.3lf', "optional" : True}],
        ["obliquity_angle", "Nominal Obliquity Angle", 6, float,
         {'frmt' : '%06.3lf', "optional" : True}],
        ["az_of_obliquity", "Azimuth of Obliquity", 7, float,
         {'frmt' : '%07.3lf', "optional" : True}],
        ["atm_refr_flag", "Atmospheric Refraction Flag", 1, int,
         {"default" : 1}],
        ["vel_aber_flag", "Velocity Aberration Flag", 1, int, {"default" : 1}],
        ["grd_cover", "Ground cover Flag", 1, int, {"default" : 9}],
        ["snow_depth_category", "Snow Depth Category", 1, int, {"default" : 9}],
        ["sun_azimuth", "Sun Azimuth Angle", 7, float,
         {'frmt' : '%-7.3lf', "optional" : True}],
        ["sun_elevation", "Sun Elevation Angle", 7, float,
         {'frmt' : '%07.3lf', "optional" : True}],
        ["predicted_niirs",
         "NIIRS Value for the Mono Collection of Principal Target", 3, float,
         {'frmt' : '%02.1lf', "optional" : True}],
        ["circl_err", "Circular Error", 5, float,
         {'frmt' : '%05.1lf', "optional" : True}],
        ["linear_err", "Linear Error", 5, float,
         {'frmt' : '%05.1lf', "optional" : True}],
        ["cloud_cover", "Cloud Cover", 3, int, {"optional" : True}],
        ["rolling_shutter_flag", "Rolling Shutter Flag", 1, int,
         {'condition': 'f.sensor_type=="F"', "optional" : True}],
        ["ue_time_flag", "Time Un-Modeled Error Flag", 1, int,
         {"optional" : True}],
        ["reserved_len", "Size of the Reserved Field", 5, int],
        ["reserved", "Reserved Data Field", "f.reserved_len", None, {'field_value_class' : FieldData}],
]

TreCSEXRB = create_nitf_tre_structure("TreCSEXRB",desc,hlp=hlp)

__all__ = [ "TreCSEXRB" ]
