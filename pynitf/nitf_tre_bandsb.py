from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the BANDSB TRE, blah. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002 V4.0, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

BANDSB is documented at blah.
'''
desc = ["BANDSB",
        ["count", "Number of Bands", 5, int],
        ["radiometric_quantity", "Data Representation", 24, str],
        ["radiometric_quantity_unit", "Data Representation Unit", 1, str],
        ["row_gsd", "Row Ground Sample Distance", 7, int],
        ["row_gsd_unit", "Units of Row Ground Sample Distance", 1, str],
        ["col_gsd", "Column Ground Sample Distance", 7, int],
        ["col_gsd_unit", "Units of Column Ground Sample Distance", 1, str],
        ["spt_resp_row", "Spatial Response Function (Rows)", 7, int],
        ["spt_resp_unit_row", "Units of Spatial Response Function (Rows)", 1, str],
        ["spt_resp_col", "Spatial Response Function (Cols)", 7, int],
        ["spt_resp_unit_col", "Units of Spatial Response Function (Cols)", 1, str],
        ["radiometric_adjustment_surface", "Adjustment Surface", 24, str,
         {'condition': "f.existence_mask & 0x80000000"}],
        ["diameter", "Diameter of the lens", 7, int, {'condition': "f.existence_mask & 0x40000000"}],
        ["wave_length_unit", "Wave Length Units", 1, str, {'condition': "f.existence_mask & 0x01F80000"}],
        [
            ["loop", "f.count"],
            ["bandid", "Band n Identifier", 50, str, {'condition': "f.existence_mask & 0x10000000"}],
            ["bad_band", "Bad Band Flag", 1, int, {'condition': "f.existence_mask & 0x08000000"}],
            ["niirs", "NIIRS Value", 3, int, {'condition': "f.existence_mask & 0x04000000"}],
            ["focal_len", "Band n Focal length", 5, int, {'condition': "f.existence_mask & 0x02000000"}],
            ["cwave", "Band n Center Response Wavelength", 7, int, {'condition': "f.existence_mask & 0x01000000"}],
            ["fwhm", "Band n Width", 7, int, {'condition': "f.existence_mask & 0x00800000"}],
            ["fwhm_unc", "Band n Width Uncertainty", 7, int, {'condition': "f.existence_mask & 0x00400000"}],
            ["nom_wave", "Band n Nominal Wavelength", 7, int, {'condition': "f.existence_mask & 0x00200000"}],
            ["nom_wave_unc", "Band n Nominal Wavelength Uncertainty", 7, int,
             {'condition': "f.existence_mask & 0x00100000"}],
            ["lbound", "Band n Lower Wavelength Bound", 7, int, {'condition': "f.existence_mask & 0x00080000"}],
            ["ubound", "Band n Upper Wavelength Bound", 7, int, {'condition': "f.existence_mask & 0x00080000"}],
            ["start_time", "Start Time", 16, str, {'condition': "f.existence_mask & 0x00020000"}],
            ["int_time", "Integration Time", 6, int, {'condition': "f.existence_mask & 0x00010000"}],
            ["caldrk", "Band n Calibration (Dark)", 6, int, {'condition': "f.existence_mask & 0x00008000"}],
            ["calibration_sensitivity", "Band n Calibration (Increment)", 5, int,
             {'condition': "f.existence_mask & 0x00008000"}],
            ["row_gsd", "Band n Spatial Response Interval (Row)", 7, int,
             {'condition': "f.existence_mask & 0x00004000"}],
            ["row_gsd_unc", "Band n Spatial Response Interval Uncertainty (Row)", 7, int,
             {'condition': "f.existence_mask & 0x00002000"}],
            ["row_gsd_unit", "Unit of Row Spacing", 1, str],
            ["col_gsd", "Band n Spatial Response Interval (Col)", 7, int],
            ["col_gsd_unc", "Band n Spatial Response Interval Uncertainty (Col)", 7, int,
             {'condition': "f.existence_mask & 0x00002000"}],
            ["col_gsd_unit", "Unit of Column Spacing", 1, str],
            ["bknoise", "Band n Background Noise", 5, int, {'condition': "f.existence_mask & 0x00001000"}],
            ["scnnoise", "Band n Scene Noise", 5, int, {'condition': "f.existence_mask & 0x00001000"}],
            ["spt_resp_function_row", "Band n Spatial Response Function (Row)", 7, int,
             {'condition': "f.existence_mask & 0x00000800"}],
            ["spt_resp_unc_row", "Band n Spatial Response Function Uncertainty (Row)", 7, int,
             {'condition': "f.existence_mask & 0x00000400"}],
            ["spt_resp_unit_row", "Unit of Spatial Response (Row)", 1, str],
            ["spt_resp_function_col", "Band n Spatial Response Function (Col)", 7, int],
            ["spt_resp_unc_col", "Band n Spatial Response Function Uncertainty (Col)", 7, int,
             {'condition': "f.existence_mask & 0x00000400"}],
            ["spt_resp_unit_col", "Unit of Spatial Response (Col)", 1, str],
        ],
        ["num_aux_b", "Number of Auxiliary Band Level Parameters (m)", 2, int,
         {'condition': "f.existence_mask & 0x00000001"}],
        ["num_aux_c", "Number of Auxiliary Cube Level Parameters (k)", 2, int,
         {'condition': "f.existence_mask & 0x00000001"}],
        [["loop", "f.num_aux_b", {'condition': "f.existence_mask & 0x00000001"}],
         ["bapf", "Band Auxiliary Parameter Value Format", 1, str, {'condition': "f.existence_mask & 0x00000001"}],
         ["ubap", "Unit of Band Auxiliary Parameter", 7, str, {'condition': "f.existence_mask & 0x00000001"}],
         [["loop", "f.count", {'condition': "f.existence_mask & 0x00000001"}],
          ["apn", "Auxiliary Parameter Integer Value", 10, int, {'condition': "f.bapf eq I"}],
          ["apa", "Auxiliary Parameter ASCII Value", 20, int, {'condition': "f.bapf eq A"}],
          ],
         ],
        [["loop", "f.num_aux_c"],
         ["capf", "Cube Auxiliary Parameter Value Format", 1, str],
         ["ucap", "Unit of Cube Auxiliary Parameter", 7, str],
         ["apn", "Auxiliary Parameter Integer Value", 10, int, {'condition': "f.capf eq I"}],
         ["apa", "Auxiliary Parameter ASCII Value", 20, int, {'condition': "f.capf eq A"}],
         ],
        ]

TreBANDSB = create_nitf_tre_structure("TreBANDSB",desc,hlp=hlp)

