from __future__ import print_function
from .nitf_field import *
from .nitf_des import *
from .nitf_des_csattb import udsh, add_uuid_des_function
import six

hlp = '''This is a NITF CSCSDB DES. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in a separate DRAFT document for the SNIP standard.
'''

_quat_format = "%+18.15lf"

desc2 =["CSCSDB",
        ['cov_version_date', 'Covariance Version Date', 8, str],
        ['core_sets', "Number of Core Sets", 1, int],
        [['loop', 'f.core_sets'],
         ["ref_frame_position", "Reference Frame for Position Coordinate Syste of the nth Core Set", 1, int],
         ["ref_frame_attitude", "Reference Frame for Attitude Coordinate Syste of the nth Core Set", 1, int],
         ["num_groups", "Number of Interdependent Sensor Error Parameter Groups of the nth Core Set", 1, int],
         [['loop', 'f.num_groups[i1]'],
          ["corr_ref_date", "Date of last De-Correlation Event for the jth Correlated Parameter Group of the nth Core Set", 8, str],
          ["corr_ref_time", "UTC Timestamp of the Last De-Correlation Event fo the jth Correlated Parameter Group of the nth Core set", 16, float, {"frmt": "%016.9lf"}],
          ["num_adj_parm", "Number of Adjustable Parameters in the jth Correlated Parameter Group of the nth Core Set", 1, int],
          [['loop', "f.num_adj_parm[i1,i2]"],
           ["adj_parm_id", "Identity of the kth Fundamental Adjustable Parameters", 1, int],
          ], # End f.num_adj_parm[i1,i2]
          ["basic_sub_alloc", "Flag Indicating Sub-Allocation of Fundamental Adjustable Parameters in the jth Group to Basic Adjustable Parameters", 1, int],
          [['loop', "int((f.num_adj_parm[i1,i2] / 2) * (f.num_adj_parm[i1,i2]+1)) if f.basic_sub_alloc[i1,i2] == 1 else 0"],
           ["errcov_c1", "Individual Error Covariance Terms", 21, float,
            {"frmt": "%+15.14le"}],
           ], # End int((f.num_adj_parm[i1,i2] / 2) * (f.num_adj_parm[i1,i2]+1))
          ["basic_pf_flag", "Flag to Identify if SPDCF of Type \"PF\" is Provided for the jth Correlated Parameter Group", 1, int,
           {"condition" : "f.basic_sub_alloc[i1,i2] == 1"}],
          ["num_basic_pf", "Number of the \"PF\" Typed SDPCF Being Provided in the jth group", 2, int,
           {"condition" : "f.basic_sub_alloc[i1,i2] == 1 and f.basic_pf_flag[i1, i2] == 1"}],
          [["loop", "f.num_basic_pf[i1,i2] if(f.basic_sub_alloc[i1,i2] == 1 and f.basic_pf_flag[i1, i2] == 1) else 0"],
           ["basic_pf_spdcf", "Identifier of the kth Basic SPDCF of Platform Type of the jth Correlated Parameter Group", 2, int],
           ["num_pairings_basic_pf", "Number of Sensor Pairing to Which the kth SDPCF of Platform Type Applies", 2, int],
           [["loop", "f.num_pairings_basic_pf[i1,i2,i3]"],
            ["basic_pf_sdpcf_sensor", "Identifier of the Other Sensor to Which this SPDCF Applies", 6, str],
            ], # End f.num_pairings_basic_pf[i1,i2,i3]
          ], # End f.num_basic_pf[i1,i2]

          ["basic_pl_flag", "Flag to Identify if SPDCF of Type \"PL\" is Provided for the jth Correlated Parameter Group", 1, int,
           {"condition" : "f.basic_sub_alloc[i1,i2] == 1"}],
          ["num_basic_pl", "Number of the \"PL\" Typed SDPCF Being Provided in the jth group", 2, int,
           {"condition" : "f.basic_sub_alloc[i1,i2] == 1 and f.basic_pl_flag[i1, i2] == 1"}],
          [["loop", "f.num_basic_pl[i1,i2] if(f.basic_sub_alloc[i1,i2] == 1 and f.basic_pl_flag[i1, i2] == 1) else 0"],
           ["basic_pl_spdcf", "Identifier of the kth Basic SPDCF of Platform Type of the jth Correlated Parameter Group", 2, int],
           ["num_pairings_basic_pl", "Number of Sensor Pairing to Which the kth SDPCF of Platform Type Applies", 2, int],
           [["loop", "f.num_pairings_basic_pl[i1,i2,i3]"],
            ["basic_pl_sdpcf_sensor", "Identifier of the Other Sensor to Which this SPDCF Applies", 6, str],
            ], # End f.num_pairings_basic_pl[i1,i2,i3]
          ], # End f.num_basic_pl[i1,i2]
          ["basic_sr_flag", "Flag to Identify if SPDCF of Type \"SR\" is Provided for the jth Correlated Parameter Group", 1, int,
           {"condition" : "f.basic_sub_alloc[i1,i2] == 1"}],
          ["basic_sr_spdcf", "Identifier of the Basic SDPCF of Sensor Type fo the jth Correlatated Parameter Group", 2, int,
           {"condition" : "f.basic_sub_alloc[i1,i2] == 1 and f.basic_sr_flag[i1,i2] == 1"}],
          ["post_sub_alloc", "Flag Indicating Sub-Allocation to Correction Posts for the jth Correlated Parameter Group", 1, int],
          ["post_start_date", "Date of First Post", 8, str,
           {"condition" : "f.post_sub_alloc[i1,i2] == 1"}],
          ["post_start_time", "Time of First Post", 15, float,
           {"condition" : "f.post_sub_alloc[i1,i2] == 1",
            "frmt" : "%15.9lf"}],
          ["post_dt", "Time between Posts", 13, float,
           {"condition" : "f.post_sub_alloc[i1,i2] == 1",
            "frmt" : "%13.9lf"}],
          ["num_posts", "Number of Posts", 3, int,
           {"condition" : "f.post_sub_alloc[i1,i2] == 1"}],
          ["common_posts_cov", "Common Correction Posts Error Covariance Flag",
           1, int,
           {"condition" : "f.post_sub_alloc[i1,i2] == 1"}],
          [['loop', "int((f.num_adj_parm[i1,i2] / 2) * (f.num_adj_parm[i1,i2]+1)) if (f.post_sub_alloc[i1,i2] == 1 and f.common_posts_cov[i1,i2] == 1) else 0"],
           ["errcov_c2", "Individual Error Covariance Terms", 21, float,
            {"frmt": "%+15.14le"}],
           ], # End int((f.num_adj_parm[i1,i2] / 2) * (f.num_adj_parm[i1,i2]+1))
          [['loop', "f.num_posts[i1,i2] if (f.post_sub_alloc[i1,i2] == 1 and f.common_posts_cov[i1,i2] == 0) else 0"],
            [['loop', "int((f.num_adj_parm[i1,i2] / 2) * (f.num_adj_parm[i1,i2]+1)) if (f.post_sub_alloc[i1,i2] == 1 and f.common_posts_cov[i1,i2] == 0) else 0"],
             # Called errcov_c2 in documentation, but we can't handle duplicate
             # names in our code. So give this a different name
             ["errcov_c2_1", "Individual Error Covariance Terms", 21, float,
              {"frmt": "%+15.14le"}],
            ], # End int((f.num_adj_parm[i1,i2] / 2) * (f.num_adj_parm[i1,i2]+1))
          ], # End f.num_posts[i1,i2]
          ["post_interp", "Post Interpolation Method", 1, int,
           {"condition" : "f.post_sub_alloc[i1,i2] == 1"}],
          ["post_pf_flag", "Flag to identify if a Post SPDCF of Type \"PF\" is Provided", 1, int, {"condition" : "f.post_sub_alloc[i1,i2] == 1"}],
          ["num_post_pf", "Number of \"PF\" Type Post SPDCF Being Provided", 1, int, {"condition" : "f.post_sub_alloc[i1,i2] == 1 and f.post_pf_flag[i1,i2] == 1"}],
          [["loop", "f.num_post_pf[i1,i2]"],
           ["post_pf_spdcf", "Identifier of the kth Post SPDCF of Platform Type for the jth Correlated Parameter Group", 2, int, {"condition" : "f.post_sub_alloc[i1,i2] == 1 and f.post_pf_flag[i1,i2] == 1"}],
           ["num_pairings_post_pf", "Number of Sensor Pairings to Which the kth Post SPDCF of Platform Type Applies", 2, int, {"condition" : "f.post_sub_alloc[i1,i2] == 1 and f.post_pf_flag[i1,i2] == 1"}],
           [["loop", "f.num_pairings_post_pf[i1,i2,i3]"],
            ["post_pf_spdcf_sensor", "Identifier of Other Sensos to With the Post SDPCF Applies", 6, str],
            ], # End f.num_pairings_post_pf[i1,i2,i3]
           ], #End f.num_post_pf[i1,i2]
          ["post_pl_flag", "Flag to identify if a Post SPDCF of Type \"PL\" is Provided", 1, int, {"condition" : "f.post_sub_alloc[i1,i2] == 1"}],
          ["num_post_pl", "Number of \"PL\" Type Post SPDCF Being Provided", 1, int, {"condition" : "f.post_sub_alloc[i1,i2] == 1 and f.post_pl_flag[i1,i2] == 1"}],
          [["loop", "f.num_post_pl[i1,i2]"],
           ["post_pl_spdcf", "Identifier of the kth Post SPDCF of Platform Type for the jth Correlated Parameter Group", 2, int, {"condition" : "f.post_sub_alloc[i1,i2] == 1 and f.post_pl_flag[i1,i2] == 1"}],
           ["num_pairings_post_pl", "Number of Sensor Pairings to Which the kth Post SPDCF of Platform Type Applies", 2, int, {"condition" : "f.post_sub_alloc[i1,i2] == 1 and f.post_pl_flag[i1,i2] == 1"}],
           [["loop", "f.num_pairings_post_pl[i1,i2,i3]"],
            ["post_pl_spdcf_sensor", "Identifier of Other Sensos to With the Post SDPCF Applies", 6, str],
            ], # End f.num_pairings_post_pl[i1,i2,i3]
           ], #End f.num_post_pl[i1,i2]
          ["post_sr_flag", "Flag to identify if a Post SPDCF of Type \"SR\" is Provided", 1, int, {"condition" : "f.post_sub_alloc[i1,i2] == 1"}],
          ["post_sr_spdcf", "Identifier of the kth Post SPDCF of Platform Type for the jth Correlated Parameter Group", 2, int, {"condition" : "f.post_sub_alloc[i1,i2] == 1 and f.post_sr_flag[i1,i2] == 1"}],
          ["post_corr", "Intr-Image Correlation Only Flag", 1, int, {"condition" : "f.post_sub_alloc[i1,i2] == 1 and f.post_sr_flag[i1,i2] == 1"}],
         ], # End f.num_groups[i1]
        ], # End f.core_sets
        ["io_cal_ap", "IO Calibration Adjustable Parameter Flag", 1, int],
        ["num_sets_cal_ap", "Number of Sets of Calibration Adjustable Parameters", 2, int, {"condition" : "f.io_cal_ap == 1"}],
        [["loop", "f.num_sets_cal_ap"],
         ["focal_length_cal", "Focal Length Associated with the nth Set of Calibration Adjustable Parameters", 11, float, {"frmt" : "%11.8lf"}],
         ], # End f.num_sets_cal_ap
        ["ncal_cpg", "Number of Correlated Parameter Groups", 2, int,{"condition" : "f.io_cal_ap == 1"}],
#        [["loop", "f.ncal_cpg"],
#         ["corr_ref_date_io", "Date of Last De-Correlation Event for the nth Correlated Parameter Group", 8, str],
# Bunch left         
        ["ts_cal_ap", "Time Synch Calibration Adjustable Parameter Flag", 1, int],
# Bunch left
        ["ue_flag", "Unmodeled Error Flag", 1, int],
        ["line_dimension", "Number of Grid Points in the Line Dimension", 3, int, {"condition" : "f.ue_flag == 1"}],
        ["sample_dimension", "Number of Grid Points in the Sample Dimension", 2, int, {"condition" : "f.ue_flag == 1"}],
        [["loop", "f.line_dimension"],
         [["loop", "f.sample_dimension"],
           ["urr", "Unmodeled Error Covariance Element (1,1)", 21, float,
            {"frmt": "%+15.14le"}],
           ["urc", "Unmodeled Error Covariance Element (1,2)", 21, float,
            {"frmt": "%+15.14le"}],
           ["ucc", "Unmodeled Error Covariance Element (2,2)", 21, float,
            {"frmt": "%+15.14le"}],
            ], # End loop f.sample_dimension
         ], # End loop f.line_dimension
        ["line_spdcf", "SPDCF Identifier for the Unmodeled Error in the Line Direction", 2, int, {"condition" : "f.ue_flag == 1"}],
        ["sample_spdcf", "SPDCF Identifier for the Unmodeled Error in the Sample Direction", 2, int, {"condition" : "f.ue_flag == 1"}],
        ["spdcf_flag", "SPDCF Flag", 1, int],
        ["num_spdcf", "Number of SPDCF", 2, int,
         { "condition" : "f.spdcf_flag == 1"}],
        [["loop", "f.num_spdcf"],
         ["spdcf_id", "SPDCF Identification Number", 2, int],
         ["spdcf_p", "Number of constituent SPDCFs associated with the SPDCF ID", 2, int],
         [["loop", "f.spdcf_p[i1]"],
          ["spdcf_fam", "SDPCF Family identification", 1, int],
          ["spdcf_weight", "Weighting of the jth constituent SPDCF",
           5, float, {"frmt" : "%05.3lf"}],
          ["fp_n", "CSM Four Parameter Correlation Function Parameter A",
           8, float,
           {"condition" : "f.spdcf_fam[i1,i2] == 0", "frmt" : "%7.6lf"}],
          ["fp_alpha", "CSM Four Parameter Correlation Function Parameter alpha",
           8, float,
           {"condition" : "f.spdcf_fam[i1,i2] == 0", "frmt" : "%7.6lf"}],
          ["fp_beta", "CSM Four Parameter Correlation Function Parameter beta",
           9, float,
           {"condition" : "f.spdcf_fam[i1,i2] == 0", "frmt" : "%8.7lf"}],
          ["fp_t", "CSM Four Parameter Correlation Function Parameter T",
           21, float,
           {"condition" : "f.spdcf_fam[i1,i2] == 0", "frmt" : "%16.15le"}],
          ["num_segs", "Number of Segments in the Piece-Wise Linear Correlation Model", 2, int,
           {"condition" : "f.spdcf_fam[i1,i2] == 1"}],
          [["loop", "f.num_segs[i1,i2]"],
           ["pl_max_cor", "Piece-Wise Linear Function Segment Maximum Correlation Value", 8, float, {"frmt" : "%7.6lf"}],
           ["pl_tau_max_cor", "Piece-Wise Linear Function Difference (Tau Segment Value)", 21, float, {"frmt" : "%16.15le"}],
          ],
          ["dc_a", "Damped Cosine Correlation Function Parameter A",
           8, float,
           {"condition" : "f.spdcf_fam[i1,i2] == 2", "frmt" : "%7.6lf"}],
          ["dc_t", "Damped Cosine Correlation Function Parameter T",
           21, float,
           {"condition" : "f.spdcf_fam[i1,i2] == 2", "frmt" : "%16.15le"}],
          ["dc_p", "Damped Cosine Correlation Function Parameter P",
           21, float,
           {"condition" : "f.spdcf_fam[i1,i2] == 2", "frmt" : "%16.15le"}],
         ], # End loop f.spdcf_p[i1]
        ], # End loop f.num_spdcf
        ["direct_covariance_flag", "Direct Covariance Flag", 1, int],
        ["dc_type", "Direct Covariance Type Flag", 1, int,
         {"condition" : "f.direct_covariance_flag == 1"}],
        ["num_para", "Total Number of Adjustable Parameters Described in the Covariance Support Data", 4, int,
         {"condition" : "f.dc_type == 0"}],
        [["loop", "f.num_para"],
         ["ad", "nth Adjustable Value Obtained by an External Adjustment",
          21, float, {"frmt": "%16.15le"}],
         ],
        [["loop", "int((f.num_para / 2) * (f.num_para +1)) if(f.dc_type == 0) else 0"],
         ["errcov_c4", "Individual Adjustable Parameter Error Covariance Terms",
          21, float, {"frmt" : "%16.15le"}],
        ],
        ["reserved_len", "Length of Reserved Portion", 9, int,
         {"default" : 0}],
        ["reserved", "Reserved Data Field", "f.reserved_len", None, {'field_value_class' : FieldData}],
]        

#print (desc2)

# udsh here is a from nitf_des_csattb, since the same user defined subheader
# is used for both
(DesCSCSDB, DesCSCSDB_UH) = create_nitf_des_structure("DesCSCSDB", desc2, udsh, hlp=hlp)

DesCSCSDB.desid = hardcoded_value("CSCSDB")
DesCSCSDB.desver = hardcoded_value("01")

def _summary(self):
    res = six.StringIO()
    print("CSCSDB", file=res)
    return res.getvalue()

DesCSCSDB.summary = _summary

add_uuid_des_function(DesCSCSDB)    
register_des_class(DesCSCSDB)
__all__ = ["DesCSCSDB", "DesCSCSDB_UH"]
