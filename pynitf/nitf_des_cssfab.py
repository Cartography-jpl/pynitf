from __future__ import print_function
from .nitf_field import *
from .nitf_des import *
from .nitf_des_csattb import udsh
import six

hlp = '''This is a NITF CSSFAB DES. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in a separate DRAFT document for the SNIP standard.
'''

_quat_format = "%+18.15lf"

desc2 =["CSSFAB",
        ['sensor_type', 'Sensor Type', 1, str],
        ['band_type', 'Spectral Band Category', 1, str],
        ['band_wavelength', 'Reference wavelength', 11, float,
         {'frmt': '%02.8lf'}],
        ['n_bands', "Number bands", 5, int, {'frmt' : '%05d'}],
        [["loop","f.n_bands"],
         ["band_index", "Band Order Index of the nth Spectral Band of the Associated Image Segments", 5, int, {'frmt' : '%05d'}],
         ["irepband", "Band-Specific Representation of the nth Band of the Associated Image Segments", 2, str],
         ["isubcat", "Band-Specific Sub-Category of the nth Band of the Associated Image Segments", 6, str],
         ],
        ['num_fl_pts', "Number of Focal Length Points", 3, int, {'frmt' : '%03d'}],
        ['fl_interp', "Focal Length Interpolation Type", 1, int],
        ['foc_length_date', "Focal Length Date", 8, str],
        [["loop","f.num_fl_pts"],
         ['foc_length_time', "Focal Length Time", 15, str],
         ['foc_length', "Focal Length Value", 11, float, {'frmt' : "%011.8lf"}],
        ],
        ['ppoff_x', "X-Component of Primary Mirror Vertex Offset", 10, float, {'frmt' : "%+010.6lf"}],
        ['ppoff_y', "Y-Component of Primary Mirror Vertex Offset", 10, float, {'frmt' : "%+010.6lf"}],
        ['ppoff_z', "Z-Component of Primary Mirror Vertex Offset", 10, float, {'frmt' : "%+010.6lf"}],
        ['angoff_x', "X-Component of Angular Sensor Frame Offset", 10, float, {'frmt' : "%+010.7lf"}],
        ['angoff_y', "Y-Component of Angular Sensor Frame Offset", 10, float, {'frmt' : "%+010.7lf"}],
        ['angoff_z', "Z-Component of Angular Sensor Frame Offset", 10, float, {'frmt' : "%+010.7lf"}],
        ['smpl_num_first', "Sample Number of the First Field Alignment of the First Pair", 12, float, {'frmt' : "%+012.5lf", "condition" : "f.sensor_type=='S'"}],
        ['delta_smpl_pair', "Delta Samples to the Corresponding Sample of Successive Pairs", 11, float, {'frmt' : "%011.5lf", "condition" : "f.sensor_type=='S'"}],
        ['num_fa_pairs', "Number of Field Alignment Pairs", 3, int, {'frmt' : "%03d", "condition" : "f.sensor_type=='S'"}],
        [["loop", "f.num_fa_pairs", {"condition" : "f.sensor_type=='S'"}],
         ['start_falign_x', "X position of the Start of the nth Field Alignment Pair", 11, float, {'frmt' : "%+011.7lf"}],
         ['start_falign_y', "Y position of the Start of the nth Field Alignment Pair", 11, float, {'frmt' : "%+011.7lf"}],
         ['end_falign_x', "X position of the End of the nth Field Alignment Pair", 11, float, {'frmt' : "%+011.7lf"}],
         ['end_falign_y', "Y position of the End of the nth Field Alignment Pair", 11, float, {'frmt' : "%+011.7lf"}],
         ],
        ["num_sets_fa_data", "Number of Sets of Field Angle Data", 1, int,
         {'condition' : "f.sensor_type=='F'"}],
        ["field_angle_type", "Field Angle Type", 1, int,
         {'condition' : "f.sensor_type=='F'"}],
        ["fa_interp", "Field Angle Interpolation Type", 1, int,
         {'condition' : "f.sensor_type=='F'"}],
        [["loop", "f.num_sets_fa_data", {"condition" : "f.sensor_type=='F' and f.field_angle_type==0"}],
         ["fl_cal", "Focal Length Associated wit hthe nth Set of Field Angle Data",
          11, float,{'frmt' : "%+011.8lf"}],
         ["number_fir_line", "First Line Number of the First Block of Field Alignment Data",
          12, float,{'frmt' : "%+012.5lf"}],
         ["delta_line", "Delta Lines of the Corresponding Line of Successive Blocks",
          11, float,{'frmt' : "%011.5lf"}],
         ],
       ]

#print (desc2)

# udsh here is a from nitf_des_csattb, since the same user defined subheader
# is used for both
(DesCSSFAB, DesCSSFAB_UH) = create_nitf_des_structure("DesCSSFAB", desc2, udsh, hlp=hlp, data_after_allowed=True)
# Temp data_after_allowed

DesCSSFAB.desid = hardcoded_value("CSSFAB")
DesCSSFAB.desver = hardcoded_value("01")

def _summary(self):
    res = six.StringIO()
    print("CSSFAB", file=res)
    return res.getvalue()

DesCSSFAB.summary = _summary

register_des_class(DesCSSFAB)
__all__ = ["DesCSSFAB", "DesCSSFAB_UH"]
