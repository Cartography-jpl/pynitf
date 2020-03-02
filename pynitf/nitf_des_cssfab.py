from .nitf_field import IntFieldData, BytesFieldData, FieldStructDiff
from .nitf_des import NitfDesFieldStruct
from .nitf_segment_data_handle import NitfSegmentDataHandleSet
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
from .nitf_des_associated_user_subheader import (add_uuid_des_function,
                                                 DesAssociatedUserSubheader)
from .nitf_segment_user_subheader_handle import desid_to_user_subheader_handle
import io

hlp = '''This is a NITF CSSFAB DES. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in a separate DRAFT document for the SNIP standard.
'''

_quat_format = "%+18.15lf"

desc =[['sensor_type', 'Sensor Type', 1, str],
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
         ['foc_length_time', "Focal Length Time", 15, float, {'frmt' : "%015.9lf"}],
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
        [["loop", "f.num_fa_pairs if f.sensor_type=='S' else 0"],
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
        [["loop", "f.num_sets_fa_data if(f.sensor_type=='F' and f.field_angle_type==0) else 0"],
         ["fl_cal", "Focal Length Associated with the nth Set of Field Angle Data",
          11, float,{'frmt' : "%+011.8lf"}],
         ["number_fir_line", "First Line Number of the First Block of Field Alignment Data",
          12, float,{'frmt' : "%+012.5lf"}],
         ["delta_line", "Delta Lines of the Corresponding Line of Successive Blocks",
          11, float,{'frmt' : "%011.5lf"}],
         ['num_fa_blocks_line', "Number of Field Alignment Blocks in the Line Direction", 3, int, {'frmt' : "%03d"}],
         ["number_fir_samp", "First Sample Number of the First Block of Field Alignment Data",
          12, float,{'frmt' : "%+012.5lf"}],
         ["delta_samp", "Delta Samples of the Corresponding Line of Successive Blocks",
          11, float,{'frmt' : "%011.5lf"}],
         ['num_fa_blocks_samp', "Number of Field Alignment Blocks in the Sample Direction", 3, int, {'frmt' : "%03d"}],
         [["loop", "f.num_fa_blocks_line[i1] if(f.sensor_type=='F' and f.field_angle_type==0) else 0"],
          [["loop", "f.num_fa_blocks_samp[i1] if(f.sensor_type=='F' and f.field_angle_type==0) else 0"],
           ["fa_x1", "X-coordinate of the first of the four alignment coordinated for block jk of the nth frame field angle set", 11, float, {'frmt' : "%+11.7lf"}],
           ["fa_y1", "Y-coordinate of the first of the four alignment coordinated for block jk of the nth frame field angle set", 11, float, {'frmt' : "%+11.7lf"}],
           ["fa_x2", "X-coordinate of the second of the four alignment coordinated for block jk of the nth frame field angle set", 11, float, {'frmt' : "%+11.7lf"}],
           ["fa_y2", "Y-coordinate of the second of the four alignment coordinated for block jk of the nth frame field angle set", 11, float, {'frmt' : "%+11.7lf"}],
           ["fa_x3", "X-coordinate of the third of the four alignment coordinated for block jk of the nth frame field angle set", 11, float, {'frmt' : "%+11.7lf"}],
           ["fa_y3", "Y-coordinate of the third of the four alignment coordinated for block jk of the nth frame field angle set", 11, float, {'frmt' : "%+11.7lf"}],
           ["fa_x4", "X-coordinate of the fourth of the four alignment coordinated for block jk of the nth frame field angle set", 11, float, {'frmt' : "%+11.7lf"}],
           ["fa_y4", "Y-coordinate of the fourth of the four alignment coordinated for block jk of the nth frame field angle set", 11, float, {'frmt' : "%+11.7lf"}],
          ],
         ],
        ],
        ["num_fp_arrays_line", "Number of Focal Plane Arrays in the Line Direction", 3, int, {"condition" : "f.sensor_type=='F' and f.field_angle_type==1"}],
        ["num_fp_arrays_samp", "Number of Focal Plane Arrays in the Sample Direction", 3, int, {"condition" : "f.sensor_type=='F' and f.field_angle_type==1"}],
        [["loop", "f.num_fp_arrays_line if(f.sensor_type=='F' and f.field_angle_type==1) else 0"],
         [["loop", "f.num_fp_arrays_samp if(f.sensor_type=='F' and f.field_angle_type==1) else 0"],
          ["lsfid_trans_t0", "Image to Fidicual Transform Parameter t0", 21, float, {"frmt" : "%+21.14E"}],
          ["lsfid_trans_t1", "Image to Fidicual Transform Parameter t1", 21, float, {"frmt" : "%+21.14E"}],
          ["lsfid_trans_t2", "Image to Fidicual Transform Parameter t2", 21, float, {"frmt" : "%+21.14E"}],
          ["lsfid_trans_t3", "Image to Fidicual Transform Parameter t3", 21, float, {"frmt" : "%+21.14E"}],
          ["lsfid_trans_t4", "Image to Fidicual Transform Parameter t4", 21, float, {"frmt" : "%+21.14E"}],
          ["lsfid_trans_t5", "Image to Fidicual Transform Parameter t5", 21, float, {"frmt" : "%+21.14E"}],
          ["lsfid_trans_t6", "Image to Fidicual Transform Parameter t6", 21, float, {"frmt" : "%+21.14E"}],
          ["lsfid_trans_t7", "Image to Fidicual Transform Parameter t7", 21, float, {"frmt" : "%+21.14E"}],
          ["lsfid_trans_t8", "Image to Fidicual Transform Parameter t8", 21, float, {"frmt" : "%+21.14E"}],
          ],
         ],
        [["loop", "f.num_sets_fa_data if (f.sensor_type=='F' and f.field_angle_type==1) else 0"],
         ['fl_cal_iop', "Focal Length Associated with the nth Set of Fame Camera Field Angle Data", 11, float, {'frmt' : "%011.8lf"}],
         ["ppo_x0", "Principal Point Offset X0", 21, float, {"frmt" : "%+21.14E"}],
         ["ppo_y0", "Principal Point Offset Y0", 21, float, {"frmt" : "%+21.14E"}],
         ["rld_k0", "Radial Lens Distortion K0", 21, float, {"frmt" : "%+21.14E"}],
         ["rld_k1", "Radial Lens Distortion K1", 21, float, {"frmt" : "%+21.14E"}],
         ["rld_k2", "Radial Lens Distortion K2", 21, float, {"frmt" : "%+21.14E"}],
         ["rld_k3", "Radial Lens Distortion K3", 21, float, {"frmt" : "%+21.14E"}],
         ["dcd_p1", "Decentering Distortion Parameter P1", 21, float, {"frmt" : "%+21.14E"}],
         ["dcd_p2", "Decentering Distortion Parameter P2", 21, float, {"frmt" : "%+21.14E"}],
         ["dcd_p3", "Decentering Distortion Parameter P3", 21, float, {"frmt" : "%+21.14E"}],
         ["ad_a1", "Affine Distortion Parameter A1", 21, float, {"frmt" : "%+21.14E"}],
         ["ad_a2", "Affine Distortion Parameter A2", 21, float, {"frmt" : "%+21.14E"}],
         ["radius_of_validity", "Radius from the Principal Point to the Outermost Region where Radial Distortion Coefficients are Valid", 21, float, {"frmt" : "%+21.14E"}],
         ],
        ["telescope_optics_flag", "Flag Variable Indicating if Additional IO Parameters Set Present Due to Telescope Optics Corrections", 1, int, {"condition" : "f.sensor_type=='F'"}],
        ["num_tele_sets_fa_data", "Number of Sets of Telescope Optics Field Angle Data", 1, int, {"condition" : "f.sensor_type=='F' and f.telescope_optics_flag == 1"}],
        ["n_frames", "Total Number of Frames in Sequence", 4, None,
         {'field_value_class' : IntFieldData, 'size_not_updated' : True,
          "condition" : "f.sensor_type=='F' and f.telescope_optics_flag == 1"}],
        [["loop", "f.n_frames if (f.sensor_type=='F' and f.telescope_optics_flag == 1) else 0"],
         ["tele_trans_t0", "Frame to Telescope-Optics Transform Parameter t0", 21, float, {"frmt" : "%+21.14E"}],
         ["tele_trans_t1", "Frame to Telescope-Optics Transform Parameter t1", 21, float, {"frmt" : "%+21.14E"}],
         ["tele_trans_t2", "Frame to Telescope-Optics Transform Parameter t2", 21, float, {"frmt" : "%+21.14E"}],
         ["tele_trans_t3", "Frame to Telescope-Optics Transform Parameter t3", 21, float, {"frmt" : "%+21.14E"}],
         ["tele_trans_t4", "Frame to Telescope-Optics Transform Parameter t4", 21, float, {"frmt" : "%+21.14E"}],
         ["tele_trans_t5", "Frame to Telescope-Optics Transform Parameter t5", 21, float, {"frmt" : "%+21.14E"}],
         ["tele_trans_t6", "Frame to Telescope-Optics Transform Parameter t6", 21, float, {"frmt" : "%+21.14E"}],
         ["tele_trans_t7", "Frame to Telescope-Optics Transform Parameter t7", 21, float, {"frmt" : "%+21.14E"}],
         ],
        [["loop", "f.num_tele_sets_fa_data if (f.sensor_type=='F' and f.telescope_optics_flag == 1) else 0"],
         ['fl_cal_iop_tele', "Focal Length Associated with the nth Set of Telescope-Optics Field Angle Data", 11, float, {'frmt' : "%011.8lf"}],
         ["ppo_x0_tele", "Principal Point Offset X0", 21, float, {"frmt" : "%+21.14E"}],
         ["ppo_y0_tele", "Principal Point Offset Y0", 21, float, {"frmt" : "%+21.14E"}],
         ["rld_k0_tele", "Radial Lens Distortion K0", 21, float, {"frmt" : "%+21.14E"}],
         ["rld_k1_tele", "Radial Lens Distortion K1", 21, float, {"frmt" : "%+21.14E"}],
         ["rld_k2_tele", "Radial Lens Distortion K2", 21, float, {"frmt" : "%+21.14E"}],
         ["rld_k3_tele", "Radial Lens Distortion K3", 21, float, {"frmt" : "%+21.14E"}],
         ["dcd_p1_tele", "Decentering Distortion Parameter P1", 21, float, {"frmt" : "%+21.14E"}],
         ["dcd_p2_tele", "Decentering Distortion Parameter P2", 21, float, {"frmt" : "%+21.14E"}],
         ["dcd_p3_tele", "Decentering Distortion Parameter P3", 21, float, {"frmt" : "%+21.14E"}],
         ["ad_a1_tele", "Affine Distortion Parameter A1", 21, float, {"frmt" : "%+21.14E"}],
         ["ad_a2_tele", "Affine Distortion Parameter A2", 21, float, {"frmt" : "%+21.14E"}],
         ["radius_of_validity_tele", "Radius from the Principal Point to the Outermost Region where Radial Distortion Coefficients are Valid", 21, float, {"frmt" : "%+21.14E"}],
         ],
        ["reserved_len", "Size of the Reserved Field", 9, int, {"default" : 0}],
        ["reserved", "Reserved Data Field", "f.reserved_len", None,
         {'field_value_class' : BytesFieldData}],
]
        
class DesCSSFAB(NitfDesFieldStruct):
    __doc__ = hlp
    desc = desc
    des_tag = "CSSFAB"
    des_ver = 1
    uh_class = DesAssociatedUserSubheader
    def summary(self):
        res = io.StringIO()
        print("CSSFAB", file=res)
        return res.getvalue()


desid_to_user_subheader_handle.add_des_user_subheader("CSSFAB",
                      DesAssociatedUserSubheader)
add_uuid_des_function(DesCSSFAB)    
NitfSegmentDataHandleSet.add_default_handle(DesCSSFAB)

class CssfabDiff(FieldStructDiff):
    '''Compare two DesCSSFAB.'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("DesCSSFAB", {})

    def handle_diff(self, h1, h2, nitf_diff):
        with nitf_diff.diff_context("DesCSSFAB"):
            if(not isinstance(h1, DesCSSFAB) or
               not isinstance(h2, DesCSSFAB)):
                return (False, None)
            return (True, self.compare_obj(h1, h2, nitf_diff))

NitfDiffHandleSet.add_default_handle(CssfabDiff())

# No default configuration

_default_config = {}
NitfDiffHandleSet.default_config["DesCSSFAB"] = _default_config

__all__ = ["DesCSSFAB", ]
