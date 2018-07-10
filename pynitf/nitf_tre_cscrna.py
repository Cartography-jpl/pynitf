from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the CSCRNA TRE, blah. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002 V4.0, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

CSCRNA is documented at blah.
'''
desc = ["CSCRNA",
        ["predict_corners", "predicted corners flag", 1, str],
        ["ulcnr_lat", "lat UL", 9, int],
        ["ulcnr_long", "long UL", 10, int],
        ["ulcnr_ht", "height UL", 8, int],
        ["urcnr_lat", "lat UR", 9, int],
        ["urcnr_long", "long UR", 10, int],
        ["urcnr_ht", "height UR", 8, int],
        ["lrcnr_lat", "lat LR", 9, int],
        ["lrcnr_long", "long LR", 10, int],
        ["lrcnr_ht", "height LR", 8, int],
        ["llcnr_lat", "lat LL", 9, int],
        ["llcnr_long", "long LL", 10, int],
        ["llcnr_ht", "height LL", 8, int],
]

TreCSCRNA = create_nitf_tre_structure("TreCSCRNA",desc,hlp=hlp)

