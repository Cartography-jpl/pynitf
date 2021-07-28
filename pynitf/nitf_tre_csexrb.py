from .nitf_field import IntFieldData, BytesFieldData
from .nitf_tre import Tre, tre_tag_to_cls
from .nitf_diff_handle import NitfDiffHandleSet
import time
import uuid
import io

hlp = '''This is the CSEXRB TRE. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation.

This particular TRE is not officially adopted yet, it is part of the new
GLAS/GFM standard in the SNIP. The TRE is documented in "10c GLAS-GFM 
Supporting TREs Combined V2"

'''

_pt_format = "%+012.2lf"
_tm_format = "%+016.9lf"
_gsd_5_format = "%5.1lf"
_gsd_12_format = "%12.1lf"

desc = [["image_uuid", "UUID Assigned to Current Image Plane", 36, str],
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
         15, float, {'condition': 'f.sensor_type=="S"', "frmt" : "%015.9lf"}],
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
          'field_value_class' : IntFieldData, 'size_not_updated' : True,
          'signed' : False}],
        ["dt_size", "Byte Size of the Delta Time Values", 1, None,
         {'condition': 'f.sensor_type=="F" and f.time_stamp_loc==0',
          'field_value_class' : IntFieldData, 'size_not_updated' : True,
          'signed' : False}],
        ["number_frames", "Byte Size of the Delta Time Values", 4, None,
         {'condition': 'f.sensor_type=="F" and f.time_stamp_loc==0',
          'field_value_class' : IntFieldData, 'size_not_updated' : True,
          'signed' : False}],
        ["number_dt", "Number of Delta Time Values", 4, None,
         {'condition': 'f.sensor_type=="F" and f.time_stamp_loc==0',
          'field_value_class' : IntFieldData, 'size_not_updated' : True,
          'signed': False}],
        [["loop", "f.number_dt if(f.sensor_type=='F' and f.time_stamp_loc==0) else 0"],
         ["dt", "Delta Time Values", "f.dt_size", None,
          { 'field_value_class' : IntFieldData, 'size_not_updated' : True,
            'signed' : False}],
        ],
        ["max_gsd", "Maximum Mean Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_12_format, "optional" : True}],
        ["along_scan_gsd", "Measured Along-Scan Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_12_format, "optional" : True}],
        ["cross_scan_gsd", "Measured Cross-Scan Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_12_format, "optional" : True}],
        ["geo_scan_gsd", "Measured Geometric Mean Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_12_format, "optional" : True}],
        ["a_s_vert_gsd", "Measured Along-Scan Vertical Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_12_format, "optional" : True}],
        ["c_s_vert_gsd", "Measured Cross-Scan Vertical Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_12_format, "optional" : True}],
        ["geo_mean_vert_gsd", "Measured Geometric Mean Vertical Ground Sample Distance (GSD)",
         12, float, {"frmt" : _gsd_12_format, "optional" : True}],
        ["geo_beta_angle", "Angle Between Along-Scan and Cross-Scan Directions",
         5, float, {"frmt" : _gsd_5_format, "optional" : True}],
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
        ["reserved", "Reserved Data Field", "f.reserved_len", None, {'field_value_class' : BytesFieldData}],
]

class TreCSEXRB(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "CSEXRB"

    def summary(self):
        res = io.StringIO()
        print("TRE - CSEXRB: %d FDTs" % (self.number_dt), file=res)
        return res.getvalue()

    def assoc_elem(self, f):
        '''Find the associated elements in the given NitfFile f. Right now it
        is not clear if we should treat missing associated elements as an
        error or not. So right now we just return a "None" where we don't have
        an associated element'''
        # Put results in a hash. This lets us sort everything at the end so
        # this is in the same order as assoc_elem_id. Not sure if order matters,
        # but for now we'll preserve this
        res = {}
        asid = list(self.assoc_des_id)
        for dseg in f.des_segment:
            if(hasattr(dseg.des, "id")):
                if(dseg.des.id in asid):
                    res[dseg.des.id] = dseg.des
        r = [ res.get(id) for id in asid]
        return r

    def generate_uuid_if_needed(self):
        '''Generate a unique UUID if we don't already have one.'''
        if(self.image_uuid == ""):
            self.image_uuid = str(uuid.uuid1())
            # Sleep is just a simple way to avoid calling uuid1 too close in
            # time. Since time is one of the components in generating the uuid,
            # if we call too close in time we get the same uuid.
            time.sleep(0.01)

    def add_assoc_elem_id(self, id):
        '''Add a associated element. For convenience, we allow this to be added
        multiple times, it only gets written to the TRE once
        '''
        if id in list(self.assoc_des_id):
            return
        self.num_assoc_des += 1
        self.assoc_des_id[self.num_assoc_des - 1] = id

    def add_assoc_elem(self, f):
        if(hasattr(f, "id")):
            if(hasattr(f, "generate_uuid_if_needed")):
                f.generate_uuid_if_needed()
            self.add_assoc_elem_id(f.id)
        else:
            raise RuntimeError("Don't know how to add the associated element")

    @property
    def id(self):
        return self.image_uuid
    
_default_config = {}

# UUID change each time they are generated, so don't include in
# check
_default_config["exclude"] = ['image_uuid', 'assoc_des_id']

NitfDiffHandleSet.default_config["TRE"]["CSEXRB"] = _default_config

tre_tag_to_cls.add_cls(TreCSEXRB)    

__all__ = [ "TreCSEXRB", ]
