from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the ILLUMB TRE, Illumination Conditions.

This TRE is documented in STDI-0002-1, The Compendium of Controlled
Extensions (CE) for the National Imagery Transmission Format Standard
(NITFS) Volume 1 Tagged Record Extensions, Appendix AL Illumination
(ILLUM) Tagged Record Extensions (TRE) ILLUMA & ILLUMB Version 1.0 
10 July 2019

Although ILLUMA supports XML encoding, ILLUMB uses traditional encoding.
'''

desc = ["ILLUMB",
        ["num_bands", "Number of Bands", 4, int, {'frmt' : "%04d"}],
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

TreILLUMB = create_nitf_tre_structure("TreILLUMB",desc,hlp=hlp)

def _summary(self):
    res = six.StringIO()
    print("ILLUMB:", file=res)
    print("Number of Bands: %d" % (self.num_bands), file=res)
    print("Band Unit of Measure: %s" % (self.band_unit), file=res)
    for i in range(self.num_bands):
        print("Band %d Lower Bound: %f" % (i, self.lbound[i]), file=res)
        print("Band %d Upper Bound: %f" % (i, self.ubound[i]), file=res)
    print("Number of Other Natural Light Sources: %d" % (self.num_others), file=res)
    for i in range(self.num_others):
        print("Other Light Source %d Name: %s" % (i, self.other_name[i]), file=res)
    print("Number of ILLUMB Comments: %d" % (self.num_coms), file=res)
    for i in range(self.num_coms):
        print("Comment %d: %s" % (i, self.comment[i]), file=res)
    print("Geodetic Datum Name: %s" % (self.geo_datum), file=res)
    print("Geodetic Datum Code: %s" % (self.geo_datum_code), file=res)
    print("Ellipsoid Name: %s" % (self.ellipsoid_name), file=res)
    print("Ellipsoid Code: %s" % (self.ellipsoid_code), file=res)
    print("Vertical Datum Reference: %s" % (self.vertical_datum_ref), file=res)
    print("Code (Category) of Vertical Reference: %s" % (self.vertical_ref_code), file=res)
    print("Bit-wise Existence Mask Fields:", file=res)
    print("%5s b23 RAD_QUANTITY, RADQ_UNIT" % (str(self.existence_mask & 0x800000)), file=res)
    print("%5s b22 SUN_AZIMUTH, SUN_ELEV" % (str(self.existence_mask & 0x400000)), file=res)
    print("%5s b21 MOON_AZIMUTH, MOON_ELEV" % (str(self.existence_mask & 0x200000)), file=res)
    print("%5s b20 MOON_PHASE_ANGLE" % (str(self.existence_mask & 0x100000)), file=res)
    print("%5s b19 MOON_ILLUM_PERCENT" % (str(self.existence_mask & 0x80000)), file=res)
    print("%5s b18 OTHER_AZIMUTH, OTHER_ELEV" % (str(self.existence_mask & 0x40000)), file=res)
    print("%5s b17 SENSOR_AZIMUTH, SENSOR_ELEV" % (str(self.existence_mask & 0x20000)), file=res)
    print("%5s b16 CATS_ANGLE" % (str(self.existence_mask & 0x10000)), file=res)
    print("%5s b15 SUN_GLINT_LAT, SUN_GLINT_LON" % (str(self.existence_mask & 0x8000)), file=res)
    print("%5s b14 CATM_ANGLE" % (str(self.existence_mask & 0x4000)), file=res)
    print("%5s b13 MOON_GLINT_LAT, MOON_GLINT_LON" % (str(self.existence_mask & 0x2000)), file=res)
    print("%5s b12 SUN_ILLUM_METHOD, SUN_ILLUM" % (str(self.existence_mask & 0x1000)), file=res)
    print("%5s b11 MOON_ILLUM_METHOD, MOON_ILLUM" % (str(self.existence_mask & 0x800)), file=res)
    print("%5s b10 SOL_LUN_DIST_ADJUST, TOT_SUNMOON_ILLUM" % (str(self.existence_mask & 0x400)), file=res)
    print("%5s b9 OTHER_ILLUM_METHOD, OTHER_ILLUM" % (str(self.existence_mask & 0x200)), file=res)
    print("%5s b8 ART_ILLUM_METHOD, ART_ILLUM_MIN, ART_ILLUM_MAX" % (str(self.existence_mask & 0x100)), file=res)
    if self.existence_mask & 0x800000:
        print("Radiometric Quantity: %s" % (self.rad_quantity), file=res)
    if self.existence_mask & 0x800000:
        print("Radiometric Quantity Unit: %s" % (self.radq_unit), file=res)
    print("Number of Illumination Conditions: %d" % (self.num_illum_sets), file=res)
    for i in range(self.num_illum_sets):
        print("Illumination Condition Date and Time: %s" % (self.datetime[i]), file=res)
        print("Target Latitude: %+010.6f" % (self.target_lat[i]), file=res)
        print("Target Longitude: %+011.6f" % (self.target_lon[i]), file=res)
        print("Target Height: %+14E" % (self.target_hgt[i]), file=res)
        if self.existence_mask & 0x400000:
            print("Sun Azimuth Angle: %05.1f" % (self.sun_azimuth[i]), file=res)
            print("Sun Elevation Angle: %05.1f" % (self.sun_elev[i]), file=res)
        if self.existence_mask & 0x200000:
            print("Lunar Azimuth Angle: %05.1f" % (self.moon_azimuth[i]), file=res)
            print("Lunar Elevation Angle: %05.1f" % (self.moon_elev[i]), file=res)
        if self.existence_mask & 0x100000:
            print("Phase Angle of the Moon in Degrees: %+06.1f" % (self.moon_phase_angle[i]), file=res)
        if self.existence_mask & 0x80000:
            print("Lunar Illumination Percentage: %03d" % (self.moon_illum_percent[i]), file=res)
        if self.existence_mask & 0x40000:
            for j in range(self.num_others):
                print("Other Natural Light Source Azimuth Angle: %05.1f" % (self.other_azimuth[i,j]), file=res)
                print("Other Natural Light Source Elevation Angle: %05.1f" % (self.other_elev[i,j]), file=res)
        if self.existence_mask & 0x20000:
            print("Sensor Azimuth Angle: %05.1f" % (self.sensor_azimuth[i]), file=res)
            print("Sensor Elevation Angle: %05.1f" % (self.sensor_elev[i]), file=res)
        if self.existence_mask & 0x10000:
            print("Camera-Target-Sun Angle: %05.1f" % (self.cats_angle[i]), file=res)
        if self.existence_mask & 0x8000:
            print("Sun Glint Latitude: %+010.6f" % (self.sun_glint_lat[i]), file=res)
            print("Sun Glint Longitude: %+011.6f" % (self.sun_glint_lon[i]), file=res)
        if self.existence_mask & 0x4000:
            print("Camera-Target-Moon Angle: %05.1f" % (self.catm_angle[i]), file=res)
        if self.existence_mask & 0x2000:
            print("Moon Glint Latitude: %+010.6f" % (self.moon_glint_lat[i]), file=res)
            print("Moon Glint Longitude: %+011.6f" % (self.moon_glint_lon[i]), file=res)
        if self.existence_mask & 0x400:
            print("Solar/Lunar Distance Adjustment: %7.5f" % (self.sol_lun_dist_adjust[i]), file=res)
        for j in range(self.num_bands):
            if self.existence_mask & 0x1000:
                print("Solar Illumination Estimation Method %s" % (self.sun_illum_method[i,j]), file=res)
                print("Solar Illumination: %16E" % (self.sun_illum[i,j]), file=res)
            if self.existence_mask & 0x800:
                print("Lunar Illumination Estimation Method: %s" % (self.moon_illum_method[i,j]), file=res)
                print("Lunar Illumination: %16E" % (self.moon_illum[i,j]), file=res)
            if self.existence_mask & 0x400:
                print("Total Illumination from Sun and Moon: %16E" % (self.tot_sunmoon_illum[i,j]), file=res)
            if self.existence_mask & 0x200:
                for k in range(self.num_others):
                    print("Other Natural Light Source Illumination Estimation Method: %s" % (self.other_illum_method[i,j,k]), file=res)
                    print("Other Natural Light Source Illumination: %16E" % (self.other_illum[i,j,k]), file=res)
            if self.existence_mask & 0x100:
                print("Artificial Illumination Estimation Method: %s" % (self.art_illum_method[i,j]), file=res)
                print("Minimum Artificial Illumination: %16E" % (self.art_illum_min[i,j]), file=res)
                print("Maximum Artificial Illumination: %16E" % (self.art_illum_max[i,j]), file=res)

    return res.getvalue()

TreILLUMB.summary = _summary

__all__ = [ "TreILLUMB" ]


