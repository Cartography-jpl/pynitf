from .nitf_field import *
from .nitf_tre import *

hlp = '''This is the RSMPIA TRE, Replacement Sensor Model Polynomial 
Identification. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002 V4.0, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

RSMPIA is documented at U-6, which points to other documentation, such as
"Replacement Sensor Model Tagged Record Extensions Specification for NITF
2.1" (http://www.gwg.nga.mil/ntb/baseline/docs/RSM/RSM_NITF_TREs_v1.0_.pdf)
'''
_r0_format = "%+21.14E"

desc = ["RSMPIA",
        ["iid", "Image Identifier", 80, str, {'optional':True}],
        ["edition", "RSM Image Support Data Edition", 40, str],
        ["r0", "Low Order Poly Const Coeff for Row", 21, float, {'frmt' : _r0_format}],
        ["rx", "Low Order Poly Coff of X for Row", 21, float, {'frmt' : _r0_format}],
        ["ry", "Low Order Poly Coff of Y for Row", 21, float, {'frmt' : _r0_format}],
        ["rz", "Low Order Poly Coff of Z for Row", 21, float, {'frmt' : _r0_format}],
        ["rxx", "Low Order Poly Coff of XX for Row", 21, float, {'frmt' : _r0_format}],
        ["rxy", "Low Order Poly Coff of XY for Row", 21, float, {'frmt' : _r0_format}],
        ["rxz", "Low Order Poly Coff of XZ for Row", 21, float, {'frmt' : _r0_format}],
        ["ryy", "Low Order Poly Coff of YY for Row", 21, float, {'frmt' : _r0_format}],
        ["ryz", "Low Order Poly Coff of YZ for Row", 21, float, {'frmt' : _r0_format}],
        ["rzz", "Low Order Poly Coff of ZZ for Row", 21, float, {'frmt' : _r0_format}],
        ["c0", "Low Order Poly Const Coeff for Col", 21, float, {'frmt' : _r0_format}],
        ["cx", "Low Order Poly Coff of X for Col", 21, float, {'frmt' : _r0_format}],
        ["cy", "Low Order Poly Coff of Y for Col", 21, float, {'frmt' : _r0_format}],
        ["cz", "Low Order Poly Coff of Z for Col", 21, float, {'frmt' : _r0_format}],
        ["cxx", "Low Order Poly Coff of XX for Col", 21, float, {'frmt' : _r0_format}],
        ["cxy", "Low Order Poly Coff of XY for Col", 21, float, {'frmt' : _r0_format}],
        ["cxz", "Low Order Poly Coff of XZ for Col", 21, float, {'frmt' : _r0_format}],
        ["cyy", "Low Order Poly Coff of YY for Col", 21, float, {'frmt' : _r0_format}],
        ["cyz", "Low Order Poly Coff of YZ for Col", 21, float, {'frmt' : _r0_format}],
        ["czz", "Low Order Poly Coff of ZZ for Col", 21, float, {'frmt' : _r0_format}],
        ["rnis", "Row Number of Image Sections", 3, int],
        ["cnis", "Column Number of Image Sections", 3, int],
        ["tnis", "Total Number of Image Sections", 3, int],
        ["rssiz", "Section Size in Rows", 21, float, {'frmt' : _r0_format}],
        ["cssiz", "Section Size in Cols", 21, float, {'frmt' : _r0_format}],
]

TreRSMPIA = create_nitf_tre_structure("TreRSMPIA",desc,hlp=hlp)
                                      

__all__ = [ "TreRSMPIA" ]
