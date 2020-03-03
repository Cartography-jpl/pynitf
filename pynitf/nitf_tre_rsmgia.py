from .nitf_tre import Tre, tre_tag_to_cls

hlp = '''This is the RSMPIA TRE, Replacement Sensor Model Grid
Identification. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002 V4.0, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

RSMGIA is documented at U-6, which points to other documentation, such as
"Replacement Sensor Model Tagged Record Extensions Specification for NITF
2.1" (http://www.gwg.nga.mil/ntb/baseline/docs/RSM/RSM_NITF_TREs_v1.0_.pdf)
'''

_gr0_format = "%+21.14E"

desc = [["iid", "Image Identifier", 80, str, {'optional':True}],
        ["edition", "RSM Image Support Data Edition", 40, str],
        ["gr0", "Low Order Poly Const Coeff for Row", 21, float, {'frmt' : _gr0_format}],
        ["grx", "Low Order Poly Coeff of X for Row", 21, float, {'frmt' : _gr0_format}],
        ["gry", "Low Order Poly Coeff of Y for Row", 21, float, {'frmt' : _gr0_format}],
        ["grz", "Low Order Poly Coeff of Z for Row", 21, float, {'frmt' : _gr0_format}],
        ["grxx", "Low Order Poly Coeff of XX for Row", 21, float, {'frmt' : _gr0_format}],
        ["grxy", "Low Order Poly Coeff of XY for Row", 21, float, {'frmt' : _gr0_format}],
        ["grxz", "Low Order Poly Coeff of XZ for Row", 21, float, {'frmt' : _gr0_format}],
        ["gryy", "Low Order Poly Coeff of YY for Row", 21, float, {'frmt' : _gr0_format}],
        ["gryz", "Low Order Poly Coeff of YZ for Row", 21, float, {'frmt' : _gr0_format}],
        ["grzz", "Low Order Poly Coeff of ZZ for Row", 21, float, {'frmt' : _gr0_format}],
        ["gc0", "Low Order Poly Const Coeff for Col", 21, float, {'frmt' : _gr0_format}],
        ["gcx", "Low Order Poly Coeff of X for Col", 21, float, {'frmt' : _gr0_format}],
        ["gcy", "Low Order Poly Coeff of Y for Col", 21, float, {'frmt' : _gr0_format}],
        ["gcz", "Low Order Poly Coeff of Z for Col", 21, float, {'frmt' : _gr0_format}],
        ["gcxx", "Low Order Poly Coeff of XX for Col", 21, float, {'frmt' : _gr0_format}],
        ["gcxy", "Low Order Poly Coeff of XY for Col", 21, float, {'frmt' : _gr0_format}],
        ["gcxz", "Low Order Poly Coeff of XZ for Col", 21, float, {'frmt' : _gr0_format}],
        ["gcyy", "Low Order Poly Coeff of YY for Col", 21, float, {'frmt' : _gr0_format}],
        ["gcyz", "Low Order Poly Coeff of YZ for Col", 21, float, {'frmt' : _gr0_format}],
        ["gczz", "Low Order Poly Coeff of ZZ for Col", 21, float, {'frmt' : _gr0_format}],
        ["grnis", "Row Number of Image Sections", 3, int],
        ["gcnis", "Col Number of Image Sections", 3, int],
        ["gtnis", "Total Number of Image Sections", 3, int],
        ["grssiz", "Section Size in Rows", 21, float, {'frmt' : _gr0_format}],
        ["gcssiz", "Section Size in Cols", 21, float, {'frmt' : _gr0_format}],
]

class TreRSMGIA(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "RSMGIA"

tre_tag_to_cls.add_cls(TreRSMGIA)    

__all__ = [ "TreRSMGIA" ]
