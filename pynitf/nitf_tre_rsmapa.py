from .nitf_tre import Tre, tre_tag_to_cls

hlp = '''This is the RSMAPA TRE, blah. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002 V4.0, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

RSMAPA is documented at blah.
'''

_xuol_format = "%21.14E"

desc = [["iid", "Image Identifier", 80, str, {'optional':True}],
        ["edition", "RSM Image Support Data Edition", 40, str],
        ["tid", "Triangulation ID", 40, str, {'optional':True}],
        ["npar", "Number of Parameters", 2, int],
        ["xuol", "Local Coord Origin (XUOL)", 21, float, {'frmt' : _xuol_format}],
        ["yuol", "Local Coord Origin (YUOL)", 21, float, {'frmt' : _xuol_format}],
        ["zuol", "Local Coord Origin (ZUOL)", 21, float, {'frmt' : _xuol_format}],
        ["xuxl", "Local Coord Unit Vector (XUXL)", 21, float, {'frmt' : _xuol_format}],
        ["xuyl", "Local Coord Unit Vector (XUYL)", 21, float, {'frmt' : _xuol_format}],
        ["xuzl", "Local Coord Unit Vector (XUZL)", 21, float, {'frmt' : _xuol_format}],
        ["yuxl", "Local Coord Unit Vector (YUXL)", 21, float, {'frmt' : _xuol_format}],
        ["yuyl", "Local Coord Unit Vector (YUYL)", 21, float, {'frmt' : _xuol_format}],
        ["yuzl", "Local Coord Unit Vector (YUZL)", 21, float, {'frmt' : _xuol_format}],
        ["zuxl", "Local Coord Unit Vector (ZUXL)", 21, float, {'frmt' : _xuol_format}],
        ["zuyl", "Local Coord Unit Vector (ZUYL)", 21, float, {'frmt' : _xuol_format}],
        ["zuzl", "Local Coord Unit Vector (ZUZL)", 21, float, {'frmt' : _xuol_format}],
        ["ir0", "Image Row Constant Index", 2, int, {'optional':True}],
        ["irx", "Image Row X Index", 2, int, {'optional':True}],
        ["iry", "Image Row Y Index", 2, int, {'optional':True}],
        ["irz", "Image Row Z Index", 2, int, {'optional':True}],
        ["irxx", "Image Row X^2 Index", 2, int, {'optional':True}],
        ["irxy", "Image Row XY Index", 2, int, {'optional':True}],
        ["irxz", "Image Row XZ Index", 2, int, {'optional':True}],
        ["iryy", "Image Row Y^2 Index", 2, int, {'optional':True}],
        ["iryz", "Image Row YZ Index", 2, int, {'optional':True}],
        ["irzz", "Image Row Z^2 Index", 2, int, {'optional':True}],
        ["ic0", "Image Col Constant Index", 2, int, {'optional':True}],
        ["icx", "Image Col X Index", 2, int, {'optional':True}],
        ["icy", "Image Col Y Index", 2, int, {'optional':True}],
        ["icz", "Image Col Z Index", 2, int, {'optional':True}],
        ["icxx", "Image Col X^2 Index", 2, int, {'optional':True}],
        ["icxy", "Image Col XY Index", 2, int, {'optional':True}],
        ["icxz", "Image Col XZ Index", 2, int, {'optional':True}],
        ["icyy", "Image Col Y^2 Index", 2, int, {'optional':True}],
        ["icyz", "Image Col YZ Index", 2, int, {'optional':True}],
        ["iczz", "Image Col Z^2 Index", 2, int, {'optional':True}],
        ["gx0", "Ground X Constant Index", 2, int, {'optional':True}],
        ["gy0", "Ground Y Constant Index", 2, int, {'optional':True}],
        ["gz0", "Ground Z Constant Index", 2, int, {'optional':True}],
        ["gxr", "Ground Rotation X", 2, int, {'optional':True}],
        ["gyr", "Ground Rotation Y", 2, int, {'optional':True}],
        ["gzr", "Ground Rotation Z", 2, int, {'optional':True}],
        ["gs", "Ground Scale", 2, int, {'optional':True}],
        ["gxx", "Ground X Adj Proportional to X index", 2, int, {'optional':True}],
        ["gxy", "Ground X Adj Proportional to Y index", 2, int, {'optional':True}],
        ["gxz", "Ground X Adj Proportional to Z index", 2, int, {'optional':True}],
        ["gyx", "Ground Y Adj Proportional to X index", 2, int, {'optional':True}],
        ["gyy", "Ground Y Adj Proportional to Y index", 2, int, {'optional':True}],
        ["gyz", "Ground Y Adj Proportional to Z index", 2, int, {'optional':True}],
        ["gzx", "Ground Z Adj Proportional to X index", 2, int, {'optional':True}],
        ["gzy", "Ground Z Adj Proportional to Y index", 2, int, {'optional':True}],
        ["gzz", "Ground Z Adj Proportional to Z index", 2, int, {'optional':True}],
        [["loop", "f.npar"],
        ["parval", "Component Value", 21, float, {'frmt' : _xuol_format}],
        ],
]

class TreRSMAPA(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "RSMAPA"

tre_tag_to_cls.add_cls(TreRSMAPA)    

__all__ = [ "TreRSMAPA", ]
