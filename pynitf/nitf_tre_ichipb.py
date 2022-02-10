from .nitf_tre import Tre, tre_tag_to_cls

hlp = '''This is the ICHIPB TRE, NITF-formatted image chips.

This TRE is documented in STDI-0002-1, The Compendium of Controlled
Extensions (CE) for the National Imagery Transmission Format Standard
(NITFS) Volume 1 Tagged Record Extensions, Appendix B ICHIPB Support
Data Extension (SDE) Version 1.0/CN2 
16 November 1998
Republished: 20 December 2019 with Change Notice 2
'''


desc = [
    ["xfrm_flag", "Non-linear Transformation Flag", 2, int, {"frmt" : "%02d"}],
    ["scale_factor", "Scale Factor Relative to R0", 10, float, {"frmt": "%010.5f"}],
    ["anamrph_corr", "Anamorphic Correction Indicator", 2, int, {"frmt": "%02d"}],
    ["scanblk_num", "Scan Block Number", 2, int, {"frmt": "%02d"}],
    ["op_row_11", "Output product row number component of grid point index (1,1) for intelligent data",
     12, float, {"frmt": "%012.3f"}],
    ["op_col_11", "Output product column number component of grid point index (1,1) for intelligent data",
     12, float, {"frmt": "%012.3f"}],
    ["op_row_12", "Output product row number component of grid point index (1,2) for intelligent data",
     12, float, {"frmt": "%012.3f"}],
    ["op_col_12", "Output product column number component of grid point index (1,2) for intelligent data",
     12, float, {"frmt": "%012.3f"}],
    ["op_row_21", "Output product row number component of grid point index (2,1) for intelligent data",
     12, float, {"frmt": "%012.3f"}],
    ["op_col_21", "Output product column number component of grid point index (2,1) for intelligent data",
     12, float, {"frmt": "%012.3f"}],
    ["op_row_22", "Output product row number component of grid point index (2,2) for intelligent data",
     12, float, {"frmt": "%012.3f"}],
    ["op_col_22", "Output product column number component of grid point index (2,2) for intelligent data",
     12, float, {"frmt": "%012.3f"}],
    ["fi_row_11", "Grid point (1,1) row number in full image coordinate system",
     12, float, {"frmt": "%012.3f"}],
    ["fi_col_11", "Grid point (1,1) column number in full image coordinate system",
     12, float, {"frmt": "%012.3f"}],
    ["fi_row_12", "Grid point (1,2) row number in full image coordinate system",
     12, float, {"frmt": "%012.3f"}],
    ["fi_col_12", "Grid point (1,2) column number in full image coordinate system",
     12, float, {"frmt": "%012.3f"}],
    ["fi_row_21", "Grid point (2,1) row number in full image coordinate system",
     12, float, {"frmt": "%012.3f"}],
    ["fi_col_21", "Grid point (2,1) column number in full image coordinate system",
     12, float, {"frmt": "%012.3f"}],
    ["fi_row_22", "Grid point (2,2) row number in full image coordinate system",
     12, float, {"frmt": "%012.3f"}],
    ["fi_col_22", "Grid point (2,2) column number in full image coordinate system",
     12, float, {"frmt": "%012.3f"}],
    ["fi_row", "Full Image Number of Rows", 8, int, {"frmt": "%08d"}],
    ["fi_col", "Full Image Number of Columns", 8, int, {"frmt": "%08d"}]
]

class TreICHIPB(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "ICHIPB"

tre_tag_to_cls.add_cls(TreICHIPB)

__all__ = [ "TreICHIPB", ]
