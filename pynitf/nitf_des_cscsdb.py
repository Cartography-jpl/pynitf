from .nitf_field import BytesFieldData, FieldStructDiff
from .nitf_des import NitfDesFieldStruct
from .nitf_segment_data_handle import NitfSegmentDataHandleSet
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
from .nitf_des_associated_user_subheader import (add_uuid_des_function,
                                                 DesAssociatedUserSubheader)
from .nitf_segment_user_subheader_handle import desid_to_user_subheader_handle
import io

hlp = '''This is a NITF CSCSDB DES. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in a separate DRAFT document for the SNIP standard.
'''

_quat_format = "%+18.15lf"

desc =[['cov_version_date', 'Covariance Version Date', 8, str],
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
       [["loop", "f.num_sets_cal_ap if f.io_cal_ap == 1 else 0"],
        ["focal_length_cal", "Focal Length Associated with the nth Set of Calibration Adjustable Parameters", 11, float, {"frmt" : "%11.8lf"}],
        ], # End f.num_sets_cal_ap
       ["ncal_cpg", "Number of Correlated Parameter Groups", 2, int,{"condition" : "f.io_cal_ap == 1"}],
       [["loop", "f.ncal_cpg if f.io_cal_ap == 1 else 0"],
        ["corr_ref_date_io", "Date of Last De-Correlation Event for the nth Correlated Parameter Group", 8, str],
        ["corr_ref_time_io", "Time of Last De-Correlation Event for the nth Correlated Parameter Group", 16, float, {"frmt": "%016.9lf"}],
        ['n1cal', "Number of Calibration Adjustable Parameters in the nth Correlated Parameter Group", 2, int],
        [["loop", "f.n1cal[i1] if f.io_cal_ap == 1 else 0"],
         ["cal_ap_id", "Calibration Adjustable Parameter Identifiers", 2, int]
         ], # end f.n1cal[i1]
        [["loop", "f.num_sets_cal_ap if f.io_cal_ap == 1 else 0"],
         [["loop", "int(f.n1cal[i1] / 2) * int(f.n1cal[i1] + 1) if f.io_cal_ap == 1 else 0"],
          ["errcov_c3", "Individual Calibration Adjustable Parameter Error Covariance Terms", 21, float, {"frmt": "%+15.14le"}],
          ], # End covariance loop
         ], # End f.num_sets_cal_ap loop
        ["cal_interp", "Interpolation type for nth Group", int, 1],
        ["spdcf_id_time", "SPDCF Identifer for the nth Correlated Parameter Group in the Time Direction", int, 2],
        ["spdcf_id_fl", "SPDCF Identifer for the nth Correlated Parameter Group in the Focal Length Direction", int, 2],
        ], # End of f.ncal_cpg
       ["ts_cal_ap", "Time Synch Calibration Adjustable Parameter Flag", 1, int],
       ["num_ts_grp", "Type Synch Parameter Type Flag", 1, int,
        {"condition" : "f.ts_cal_ap == 1"}],
       ["corr_ref_date_ts1", "Date of last de-correlation event for this Type 1 Time Sync Correlated Parameter Group", 8, str,
        {"condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 1"}],
       ["corr_ref_time_ts1", "UTC Timestape of last de-correlation event for this Type 1 Time Sync Correlated Parameter Group", 16, float,
        {"frmt": "%016.9lf",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 1"}],
       ["tsrr", "Time Sync Covariance Element(1,1)", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 1"}],
       ["tsrc", "Time Sync Covariance Element(1,2)", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 1"}],
       ["tsrc", "Time Sync Covariance Element(2,2)", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 1"}],
       ["ts_spdcf1", "SPDCF Identifer for the Type 1 Tiem Sync", 2, int,
        { "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 1"}],
       ["corr_ref_date_tsp2", "Date of last de-correlation event for this Type 1 Time Sync Correlated Parameter Group", 8, str,
        {"condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 2"}],
       ["corr_ref_time_tsp2", "UTC Timestape of last de-correlation event for this Type 1 Time Sync Correlated Parameter Group", 16, float,
        {"frmt": "%016.9lf",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 2"}],
       ["ts_pos_cov2", "Type 2 Type Sync Position Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 2"}],
       ["ts_pos_spdcf2", "SPDCF Identifer for the Type 2 Time Sync", 2, int,
        { "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 2"}],
       ["corr_ref_date_tsa2", "Date of last de-correlation event for this Type 2 Time Sync Attitude Correlated Parameter Group", 8, str,
        {"condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 2"}],
       ["corr_ref_time_tsa2", "UTC Timestape of last de-correlation event for this Type 2 Time Sync Attitude Correlated Parameter Group", 16, float,
        {"frmt": "%016.9lf",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 2"}],
       ["ts_att_cov2", "Type 2 Type Sync Attitude Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 2"}],
       ["ts_att_spdcf2", "SPDCF Identifer for the Type 2 Time Sync", 2, int,
        { "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 2"}],
       ["corr_ref_date_ts3", "Date of last de-correlation event for this Type 1 Time Sync Correlated Parameter Group", 8, str,
        {"condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 3"}],
       ["corr_ref_time_ts3", "UTC Timestape of last de-correlation event for this Type 1 Time Sync Correlated Parameter Group", 16, float,
        {"frmt": "%016.9lf",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 3"}],
       ["ts_pos_cov3", "Type 3 Type Sync Position Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 3"}],
       ["ts_pos_att_cov3", "Type 3 Type Sync Position Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 3"}],
       ["ts_pos_fl_cov3", "Type 3 Type Sync Position Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 3"}],
       ["ts_att_cov3", "Type 3 Type Sync Position Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 3"}],
       ["ts_att_fl_cov3", "Type 3 Type Sync Position Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 3"}],
       ["ts_fl_cov3", "Type 3 Type Sync Position Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 3"}],
       ["ts_spdcf3", "SPDCF Identifer for the Type 3 Time Sync", 2, int,
        { "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 3"}],
       ["corr_ref_date_tspa4", "Date of last de-correlation event for this Type 1 Time Sync Correlated Parameter Group", 8, str,
        {"condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 4"}],
       ["corr_ref_time_tspa4", "UTC Timestape of last de-correlation event for this Type 1 Time Sync Correlated Parameter Group", 16, float,
        {"frmt": "%016.9lf",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 4"}],
       ["ts_pos_cov4", "Type 3 Type Sync Position Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 4"}],
       ["ts_pos_att_cov4", "Type 4 Type Sync Position Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 4"}],
       ["ts_att_cov4", "Type 3 Type Sync Attitude Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 4"}],
       ["ts_pa_spdcf4", "SPDCF Identifer for the Type 4 Time Sync", 2, int,
        { "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 4"}],
       
       ["corr_ref_date_tsfl4", "Date of last de-correlation event for this Type 5 Time Sync focal length Correlated Parameter Group", 8, str,
        {"condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 4"}],
       ["corr_ref_time_tsfl4", "UTC Timestape of last de-correlation event for this Type 4 Time Sync Focal Length Correlated Parameter Group", 16, float,
        {"frmt": "%016.9lf",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 4"}],
       ["ts_fl_cov4", "Type 4 Type Sync Focal Length Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 4"}],
       ["ts_fl_spdcf4", "SPDCF Identifer for the Type 4 Time Sync", 2, int,
        { "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 4"}],
       ["corr_ref_date_tsp5", "Date of last de-correlation event for this Type 1 Time Sync Correlated Parameter Group", 8, str,
        {"condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 5"}],
       ["corr_ref_time_tsp5", "UTC Timestape of last de-correlation event for this Type 1 Time Sync Correlated Parameter Group", 16, float,
        {"frmt": "%016.9lf",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 5"}],
       ["ts_pos_cov5", "Type 5 Type Sync Position Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 5"}],
       ["ts_pos_spdcf5", "SPDCF Identifer for the Type 5 Time Sync", 2, int,
        { "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 5"}],
       ["corr_ref_date_tsa5", "Date of last de-correlation event for this Type 5 Time Sync Attitude Correlated Parameter Group", 8, str,
        {"condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 5"}],
       ["corr_ref_time_tsa5", "UTC Timestape of last de-correlation event for this Type 5 Time Sync Attitude Correlated Parameter Group", 16, float,
        {"frmt": "%016.9lf",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 5"}],
       ["ts_att_cov5", "Type 5 Type Sync Attitude Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 5"}],
       ["ts_att_spdcf5", "SPDCF Identifer for the Type 5 Time Sync", 2, int,
        { "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 5"}],
       ["corr_ref_date_tsfl5", "Date of last de-correlation event for this Type 5 Time Sync focal length Correlated Parameter Group", 8, str,
        {"condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 5"}],
       ["corr_ref_time_tsfl5", "UTC Timestape of last de-correlation event for this Type 5 Time Sync Focal Length Correlated Parameter Group", 16, float,
        {"frmt": "%016.9lf",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 5"}],
       ["ts_fl_cov5", "Type 5 Type Sync Focal Length Adjustable Parameter Covriance", 21, float,
        {"frmt": "%+15.14le",
         "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 5"}],
       ["ts_fl_spdcf5", "SPDCF Identifer for the Type 5 Time Sync", 2, int,
        { "condition" : "f.ts_cal_ap == 1 and f.num_ts_grp == 5"}],
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
       ["reserved", "Reserved Data Field", "f.reserved_len", None, {'field_value_class' : BytesFieldData}],
]        

class DesCSCSDB(NitfDesFieldStruct):
    __doc__ = hlp
    desc = desc
    des_tag = "CSCSDB"
    des_ver = 1
    uh_class = DesAssociatedUserSubheader
    def summary(self):
        res = io.StringIO()
        print("CSCSDB", file=res)
        return res.getvalue()


desid_to_user_subheader_handle.add_des_user_subheader("CSCSDB",
                      DesAssociatedUserSubheader)
add_uuid_des_function(DesCSCSDB)    
NitfSegmentDataHandleSet.add_default_handle(DesCSCSDB)

class CsscdbDiff(FieldStructDiff):
    '''Compare two DesCSCSDB.'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("DesCSCSDB", {})

    def handle_diff(self, h1, h2, nitf_diff):
        with nitf_diff.diff_context("DesCSCSDB"):
            if(not isinstance(h1, DesCSCSDB) or
               not isinstance(h2, DesCSCSDB)):
                return (False, None)
            return (True, self.compare_obj(h1, h2, nitf_diff))

NitfDiffHandleSet.add_default_handle(CsscdbDiff())

# No default configuration

_default_config = {}
NitfDiffHandleSet.default_config["DesCSCSDB"] = _default_config

__all__ = ["DesCSCSDB", ]
