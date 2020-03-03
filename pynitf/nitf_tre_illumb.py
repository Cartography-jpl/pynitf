from .nitf_field import IntFieldData
from .nitf_tre import Tre, tre_tag_to_cls
import io

hlp = '''This is the ILLUMB TRE, Illumination Conditions.

This TRE is documented in STDI-0002-1, The Compendium of Controlled
Extensions (CE) for the National Imagery Transmission Format Standard
(NITFS) Volume 1 Tagged Record Extensions, Appendix AL Illumination
(ILLUM) Tagged Record Extensions (TRE) ILLUMA & ILLUMB Version 1.0 
10 July 2019

Although ILLUMA supports XML encoding, ILLUMB uses traditional encoding.
'''

desc = [["num_bands", "Number of Bands", 4, int, {'frmt' : "%04d"}],
        ["band_unit", "Band Unit of Measure", 40, str],
        [["loop", "f.num_bands"],
         ["lbound", "Band Lower Bound", 16, float, {'frmt' : "%16E"}],
         ["ubound", "Band Upper Bound", 16, float, {'frmt' : "%16E"}]],
        ["num_others", "Number of Other Natural Light Sources", 2, int, {'frmt' : "%02d"}],
        [["loop", "f.num_others"],
         ["other_name", "Name of the Other Light Source", 40, str]],
        ["num_coms", "Number of ILLUMB Comments", 1, int],
        [["loop", "f.num_coms"],
         ["comment", "Comment", 80, str]],
        ["geo_datum", "Geodetic Datum Name", 80, str, {'default' : "World Geodetic System 1984"}],
        ["geo_datum_code", "Geodetic Datum Code", 4, str, {'default' : "WGE"}],
        ["ellipsoid_name", "Ellipsoid Name", 80, str, {'default' : "World Geodetic System 1984"}],
        ["ellipsoid_code", "Ellipsoid Code", 3, str, {'default' : "WE"}],
        ["vertical_datum_ref", "Vertical Datum Reference", 80, str, {'default' : "Geodetic"}],
        ["vertical_ref_code", "Code (Category) of Vertical Reference", 4, str, {'default' : "GEOD"}],
        ["existence_mask", "Bit-wise Existence Mask Field", 3, None, {'field_value_class' : IntFieldData, 'size_not_updated' : True}],
        ["rad_quantity", "Radiometric Quantity", 40, str, {'condition' : "f.existence_mask & 0x800000"}],
        ["radq_unit", "Radiometric Quantity Unit", 40, str, {'condition' : "f.existence_mask & 0x800000"}],
        ["num_illum_sets", "Number of Illumination Conditions", 3, int, {'frmt' : "%03d"}],
        [["loop", "f.num_illum_sets"],
         ["datetime", "Illumination Condition Date and Time", 14, str],
         ["target_lat", "Target Latitude", 10, float, {'frmt' : "%+010.6f"}],
         ["target_lon", "Target Longitude", 11, float, {'frmt' : "%+011.6f"}],
         ["target_hgt", "Target Height", 14, float, {'frmt' : "%+14E"}],
         ["sun_azimuth", "Sun Azimuth Angle", 5, float, {'frmt': "%05.1f", 'condition' : "f.existence_mask & 0x400000"}],
         ["sun_elev", "Sun Elevation Angle", 5, float, {'frmt': "%+05.1f", 'condition' : "f.existence_mask & 0x400000"}],
         ["moon_azimuth", "Lunar Azimuth Angle", 5, float, {'frmt': "%05.1f", 'condition' : "f.existence_mask & 0x200000"}],
         ["moon_elev", "Lunar Elevation Angle", 5, float, {'frmt': "%+05.1f", 'condition' : "f.existence_mask & 0x200000"}],
         ["moon_phase_angle", "Phase Angle of the Moon in Degrees", 6, float, {'frmt': "%+06.1f", 'condition' : "f.existence_mask & 0x100000"}],
         ["moon_illum_percent", "Lunar Illumination Percentage", 3, int, {'frmt': "%03d", 'condition' : "f.existence_mask & 0x80000"}],
         [["loop", "f.num_others if (f.existence_mask & 0x40000) else 0"],
          ["other_azimuth", "Other Natural Light Source Azimuth Angle", 5, float, {'frmt': "%05.1f"}],
          ["other_elev", "Other Natural Light Source Elevation Angle", 5, float, {'frmt': "%+05.1f"}]],
         ["sensor_azimuth", "Sensor Azimuth Angle", 5, float, {'frmt' : "%05.1f", 'condition' : "f.existence_mask & 0x20000"}],
         ["sensor_elev", "Sensor Elevation Angle", 5, float, {'frmt' : "%+05.1f", 'condition' : "f.existence_mask & 0x20000"}],
         ["cats_angle", "Camera-Target-Sun Angle", 5, float, {'frmt' : "%05.1f", 'condition' : "f.existence_mask & 0x10000"}],
         ["sun_glint_lat", "Sun Glint Latitude", 10, float, {'frmt' : "%+010.6f", 'condition' : "f.existence_mask & 0x8000"}],
         ["sun_glint_lon", "Sun Glint Longitude", 11, float, {'frmt' : "%+011.6f", 'condition' : "f.existence_mask & 0x8000"}],
         ["catm_angle", "Camera-Target-Moon Angle", 5, float, {'frmt' : "%05.1f", 'condition' : "f.existence_mask & 0x4000"}],
         ["moon_glint_lat", "Moon Glint Latitude", 10, float, {'frmt' : "%+010.6f", 'condition' : "f.existence_mask & 0x2000"}],
         ["moon_glint_lon", "Moon Glint Longitude", 11, float, {'frmt' : "%+011.6f", 'condition' : "f.existence_mask & 0x2000"}],
         ["sol_lun_dist_adjust", "Solar/Lunar Distance Adjustment", 7, float, {'frmt' : "%7.5f", 'condition' : "f.existence_mask & 0x400"}],
         [["loop", "f.num_bands"],
          ["sun_illum_method", "Solar Illumination Estimation Method", 1, str, {'condition' : "f.existence_mask & 0x1000"}],
          ["sun_illum", "Solar Illumination", 16, float, {'frmt' : "%16E", 'condition' : "f.existence_mask & 0x1000"}],
          ["moon_illum_method", "Lunar Illumination Estimation Method", 1, str, {'condition' : "f.existence_mask & 0x800"}],
          ["moon_illum", "Lunar Illumination", 16, float, {'frmt' : "%16E", 'condition' : "f.existence_mask & 0x800"}],
          ["tot_sunmoon_illum", "Total Illumination from Sun and Moon", 16, float, {'frmt' : "%16E", 'condition' : "f.existence_mask & 0x400"}],
          [["loop", "f.num_others if(f.existence_mask & 0x200) else 0"],
           ["other_illum_method", "Other Natural Light Source Illumination Estimation Method", 1, str],
           ["other_illum", "Other Natural Light Source Illumination", 16, float, {'frmt' : "%16E"}]],
          ["art_illum_method", "Artificial Illumination Estimation Method", 1, str, {'condition' : "f.existence_mask & 0x100"}],
          ["art_illum_min", "Minimum Artificial Illumination", 16, float, {'frmt' : "%16E", 'condition' : "f.existence_mask & 0x100"}]],
          ["art_illum_max", "Maximum Artificial Illumination", 16, float, {'frmt' : "%16E", 'condition' : "f.existence_mask & 0x100"}]]
]

class TreILLUMB(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "ILLUMB"

tre_tag_to_cls.add_cls(TreILLUMB)    


__all__ = [ "TreILLUMB", ]


