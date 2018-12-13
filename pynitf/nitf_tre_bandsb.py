from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the BANDSB TRE. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002 V4.0, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

BANDSB is documented at blah.

!!! NOTE !!!
BANDSB takes some liberties with the data types. For some of the float types it think '.0' can just take up
2 characters. Python likes to convert '.1' to '0.1' taking up 3 characters. This means, as BANDSB is implemented now,
we lose one digit of float for a lot of these fields. We may not need that digit. If/when we do we need to revisit.
Example fields are: caldrk, calibration_sensitiviy, etc.

'''
desc = ["BANDSB",
        ["count", "Number of Bands", 5, int],
        ["radiometric_quantity", "Data Representation", 24, str],
        ["radiometric_quantity_unit", "Data Representation Unit", 1, str],
        ["cube_scale_factor", "Cube Scale Factor", 4, None, {'field_value_class' : FloatFieldData, 'size_not_updated' : True}],
        ["cube_additive_factor", "Cube Additive Factor", 4, None, {'field_value_class' : FloatFieldData, 'size_not_updated' : True}],
        ["row_gsd_nrs", "Row Ground Sample Distance", 7, str], #This field is really weird. The value is 000.001 to 9999.99
                                                    # notice the change in precision. Also, it can be ------- which
                                                    #is not a number at all. Only way to store any of that is through str
        ["row_gsd_nrs_unit", "Units of Row Ground Sample Distance", 1, str],
        ["col_gsd_ncs", "Column Ground Sample Distance", 7, str], #Same weirdness as row_gsd
        ["col_gsd_ncs_unit", "Units of Column Ground Sample Distance", 1, str],
        ["spt_resp_row_nom", "Spatial Response Function (Rows)", 7, str], #Same weirdness as row_gsd
        ["spt_resp_unit_row_nom", "Units of Spatial Response Function (Rows)", 1, str],
        ["spt_resp_col_nom", "Spatial Response Function (Cols)", 7, str], #Same weirdness as row_gsd
        ["spt_resp_unit_col_nom", "Units of Spatial Response Function (Cols)", 1, str],
        ["data_fld_1", "Field reserved for future use", 48, None, {'field_value_class' : FieldData, 'size_not_updated' : True}],
        ["existence_mask", "Bit-wise existence mask field", 4, None, {'field_value_class' : IntFieldData, 'size_not_updated' : True}],
        ["radiometric_adjustment_surface", "Adjustment Surface", 24, str, {'condition': "f.existence_mask & 0x80000000"}],
        ["atmospheric_adjustment_altitude", "Adjustment altitude above WGS84 Ellipsoid", 4, None,
         {'field_value_class' : FloatFieldData, 'size_not_updated' : True, 'condition': "f.existence_mask & 0x80000000"}],
        ["diameter", "Diameter of the lens", 7, float, {'condition': "f.existence_mask & 0x40000000", "frmt" : "%07.2f"}],
        ["data_fld_2", "Field reserved for future use", 32, None,
         {'field_value_class' : FieldData, 'size_not_updated' : True, 'condition': "f.existence_mask & 0x20000000"}],
        ["wave_length_unit", "Wave Length Units", 1, str, {'condition': "f.existence_mask & 0x01F80000"}],
        [
            ["loop", "f.count"],
            ["bandid", "Band n Identifier", 50, str, {'condition': "f.existence_mask & 0x10000000"}],
            ["bad_band", "Bad Band Flag", 1, int, {'condition': "f.existence_mask & 0x08000000"}],
            ["niirs", "NIIRS Value", 3, float, {'condition': "f.existence_mask & 0x04000000"}],
            ["focal_len", "Band n Focal length", 5, int, {'condition': "f.existence_mask & 0x02000000"}],
            ["cwave", "Band n Center Response Wavelength", 7, float, {'condition': "f.existence_mask & 0x01000000"}],
            ["fwhm", "Band n Width", 7, float, {'condition': "f.existence_mask & 0x00800000"}],
            ["fwhm_unc", "Band n Width Uncertainty", 7, float, {'condition': "f.existence_mask & 0x00400000"}],
            ["nom_wave", "Band n Nominal Wavelength", 7, float, {'condition': "f.existence_mask & 0x00200000"}],
            ["nom_wave_unc", "Band n Nominal Wavelength Uncertainty", 7, float,
             {'condition': "f.existence_mask & 0x00100000"}],
            ["lbound", "Band n Lower Wavelength Bound", 7, float, {'condition': "f.existence_mask & 0x00080000"}],
            ["ubound", "Band n Upper Wavelength Bound", 7, float, {'condition': "f.existence_mask & 0x00080000"}],
            ["scale_factor", "Individual Scale Factor", 4, None,
             {'field_value_class' : FloatFieldData, 'size_not_updated' : True, 'condition' : "f.existence_mask & 0x00040000"}],
            ["additive_factor", "Individual Additive Factor", 4, None,
             {'field_value_class' : FloatFieldData, 'size_not_updated' : True, 'condition' : "f.existence_mask & 0x00040000"}],
            ["start_time", "Start Time", 16, str, {'condition': "f.existence_mask & 0x00020000"}],
            ["int_time", "Integration Time", 6, int, {'condition': "f.existence_mask & 0x00010000"}],
            ["caldrk", "Band n Calibration (Dark)", 6, float, {'condition': "f.existence_mask & 0x00008000"}],
            ["calibration_sensitivity", "Band n Calibration (Increment)", 5, float,
             {'condition': "f.existence_mask & 0x00008000"}],
            ["row_gsd", "Band n Spatial Response Interval (Row)", 7, float,
             {'condition': "f.existence_mask & 0x00004000"}],
            ["row_gsd_unc", "Band n Spatial Response Interval Uncertainty (Row)", 7, float,
             {'condition': "f.existence_mask & 0x00002000"}],
            ["row_gsd_unit", "Unit of Row Spacing", 1, str],
            ["col_gsd", "Band n Spatial Response Interval (Col)", 7, float],
            ["col_gsd_unc", "Band n Spatial Response Interval Uncertainty (Col)", 7, float,
             {'condition': "f.existence_mask & 0x00002000"}],
            ["col_gsd_unit", "Unit of Column Spacing", 1, str],
            ["bknoise", "Band n Background Noise", 5, float, {'condition': "f.existence_mask & 0x00001000"}],
            ["scnnoise", "Band n Scene Noise", 5, float, {'condition': "f.existence_mask & 0x00001000"}],
            ["spt_resp_function_row", "Band n Spatial Response Function (Row)", 7, float,
             {'condition': "f.existence_mask & 0x00000800"}],
            ["spt_resp_unc_row", "Band n Spatial Response Function Uncertainty (Row)", 7, float,
             {'condition': "f.existence_mask & 0x00000400"}],
            ["spt_resp_unit_row", "Unit of Spatial Response (Row)", 1, str],
            ["spt_resp_function_col", "Band n Spatial Response Function (Col)", 7, float],
            ["spt_resp_unc_col", "Band n Spatial Response Function Uncertainty (Col)", 7, float,
             {'condition': "f.existence_mask & 0x00000400"}],
            ["spt_resp_unit_col", "Unit of Spatial Response (Col)", 1, str],
            ["data_fld_3", "Field reserved for future use", 16, None,
             {'field_value_class': FieldData, 'size_not_updated' : True, 'condition': "f.existence_mask & 0x00000200"}],
            ["data_fld_4", "Field reserved for future use", 24, None,
             {'field_value_class': FieldData, 'size_not_updated' : True, 'condition': "f.existence_mask & 0x00000100"}],
            ["data_fld_5", "Field reserved for future use", 32, None,
             {'field_value_class': FieldData, 'size_not_updated' : True, 'condition': "f.existence_mask & 0x00000080"}],
            ["data_fld_6", "Field reserved for future use", 48, None,
             {'field_value_class': FieldData, 'size_not_updated' : True, 'condition': "f.existence_mask & 0x00000040"}],
        ],
        ["num_aux_b", "Number of Auxiliary Band Level Parameters (m)", 2, int, {'condition': "f.existence_mask & 0x00000001"}],
        ["num_aux_c", "Number of Auxiliary Cube Level Parameters (k)", 2, int, {'condition': "f.existence_mask & 0x00000001"}],
        [["loop", "f.num_aux_b", {'condition': "f.existence_mask & 0x00000001"}],
         ["bapf", "Band Auxiliary Parameter Value Format", 1, str, {'condition': "f.existence_mask & 0x00000001"}],
         ["ubap", "Unit of Band Auxiliary Parameter", 7, str, {'condition': "f.existence_mask & 0x00000001"}],
         [["loop", "f.count", {'condition': "f.existence_mask & 0x00000001"}],
          ["apn_band", "Auxiliary Parameter Integer Value", 10, int, {'condition': "f.bapf[i1] == \"I\""}],
          ["apr_band", "Auxiliary Parameter Real Value", 4, None, {'field_value_class': FloatFieldData, 'size_not_updated' : True,'condition': "f.bapf[i1] == \"R\""}],
          ["apa_band", "Auxiliary Parameter ASCII Value", 20, int, {'condition': "f.bapf[i1] == \"A\""}],
         ],
        ],
        [["loop", "f.num_aux_c"],
         ["capf", "Cube Auxiliary Parameter Value Format", 1, str],
         ["ucap", "Unit of Cube Auxiliary Parameter", 7, str],
         ["apn_cube", "Auxiliary Parameter Integer Value", 10, int, {'condition': "f.capf[i1] == 'I'"}],
         ["apr_cube", "Auxiliary Parameter Real Value", 4, None,
          {'field_value_class': FloatFieldData, 'size_not_updated' : True, 'condition': "f.capf[i1] == 'R'"}],
         ["apa_cube", "Auxiliary Parameter ASCII Value", 20, int, {'condition': "f.capf[i1] == 'A'"}],
         ],
        ]

# Not currently working
#TreBANDSB = create_nitf_tre_structure("TreBANDSB",desc,hlp=hlp)

