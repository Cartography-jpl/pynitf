from .nitf_field import *
from .nitf_tre import *

hlp = '''This is the RSMAPB TRE,
Replacement Sensor Model Adjustable Parameters, version B.

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002 V4.0, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

RSMAPB is documented at http://www.gwg.nga.mil/ntb/baseline/docs/RSM/RSM_NITF_TREs_v1.0_.pdf.
'''

_nsfx_format = "%+21.14E"

desc = ["RSMAPB",
        ["iid", "Image Identifier", 80, str, {'optional':True}],
        ["edition", "RSM Image Support Data Edition", 40, str],
        ["tid", "Triangulation ID", 40, str],
        ["npar", "Number of Parameters", 2, int],
        ["aptyp", "Adjustable Parameter Type", 1, str],
        ["loctyp", "Local Coordinate System Identifier", 1, str],
        ["nsfx", "Normalization Scale Factor for X", 21, float, {'frmt' : _nsfx_format}],
        ["nsfy", "Normalization Scale Factor for Y", 21, float, {'frmt' : _nsfx_format}],
        ["nsfz", "Normalization Scale Factor for Z", 21, float, {'frmt' : _nsfx_format}],
        ["noffx", "Normalization Offset for X", 21, float, {'frmt' : _nsfx_format}],
        ["noffy", "Normalization Offset for Y", 21, float, {'frmt' : _nsfx_format}],
        ["noffz", "Normalization Offset for Z", 21, float, {'frmt' : _nsfx_format}],
        ["xuol", "Local Coord Origin (XUOL)", 21, float, {'frmt' : _nsfx_format}],
        ["yuol", "Local Coord Origin (YUOL)", 21, float, {'frmt' : _nsfx_format}],
        ["zuol", "Local Coord Origin (ZUOL)", 21, float, {'frmt' : _nsfx_format}],
        ["xuxl", "Local Coord Unit Vector (XUXL)", 21, float, {'frmt' : _nsfx_format}],
        ["xuyl", "Local Coord Unit Vector (XUYL)", 21, float, {'frmt' : _nsfx_format}],
        ["xuzl", "Local Coord Unit Vector (XUZL)", 21, float, {'frmt' : _nsfx_format}],
        ["yuxl", "Local Coord Unit Vector (YUXL)", 21, float, {'frmt' : _nsfx_format}],
        ["yuyl", "Local Coord Unit Vector (YUYL)", 21, float, {'frmt' : _nsfx_format}],
        ["yuzl", "Local Coord Unit Vector (YUZL)", 21, float, {'frmt' : _nsfx_format}],
        ["zuxl", "Local Coord Unit Vector (ZUXL)", 21, float, {'frmt' : _nsfx_format}],
        ["zuyl", "Local Coord Unit Vector (ZUYL)", 21, float, {'frmt' : _nsfx_format}],
        ["zuzl", "Local Coord Unit Vector (ZUZL)", 21, float, {'frmt' : _nsfx_format}],
        ["apbase", "Basis Option", 1, str],
        ["nisap", "Number of Image-Space Adjustable Parameters", 2, int, {'condition' : "f.aptyp == 'I'"}],
        ["nisapr", "Number of Image-Space Adjustable Parameters for Image Row Coordinate", 2, int, {'condition' : "f.aptyp == 'I'"}],
        [["loop", "0 if f.aptyp == 'G' else int(f.nisapr)"],
         ["xpwrr", "Row Parameter Power of X", 1, int, {'condition': "f.aptyp == 'I'"}],
         ["ypwrr", "Row Parameter Power of Y", 1, int, {'condition': "f.aptyp == 'I'"}],
         ["zpwrr", "Row Parameter Power of Z", 1, int, {'condition': "f.aptyp == 'I'"}],
        ],
        ["nisapc", "Number of Image-Space Adjustable Parameters for Image Column Coordinate", 2, int, {'condition': "f.aptyp == 'I'"}],
        [["loop", "0 if f.aptyp == 'G' else int(f.nisapc)"],
         ["xpwrc", "Column Parameter Power of X", 1, int, {'condition': "f.aptyp == 'I'"}],
         ["ypwrc", "Column Parameter Power of Y", 1, int, {'condition': "f.aptyp == 'I'"}],
         ["zpwrc", "Column Parameter Power of Z", 1, int, {'condition': "f.aptyp == 'I'"}],
        ],
        ["ngsap", "Number of Ground Adjustable Parameters", 2, int, {'condition' : "f.aptyp == 'G'"}],
        [["loop", "0 if f.aptyp == 'I' else int(f.ngsap)"],
         ["gsapid", "Ground-space Adjustable Parameter ID", 4, str, {'condition': "f.aptyp == 'G'"}]
        ],
        #This is a phantom field
        #["nbasis", "Number of Basis Adjustable Parameters"],
        [["loop", "0 if f.apbase == 'N' else int(f.npar*f.nisap) if f.aptyp == 'I' else int(f.npar*f.ngsap)"],
         ["ael", "Matrix A Element", 21, float, {'frmt' : _nsfx_format, 'condition': "f.apbase == 'Y'"}]
        ],
        [["loop", "f.npar"],
         ["parval", "Component Value", 21, float, {'frmt' : _nsfx_format}]
        ]
]

TreRSMAPB = create_nitf_tre_structure("TreRSMAPB",desc,hlp=hlp)

__all__ = [ "TreRSMAPB" ]
