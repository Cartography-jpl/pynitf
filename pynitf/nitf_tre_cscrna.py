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

_lat_frmt = '%+09.5f'
_long_frmt = '%+010.5f'
_ht_frmt = '%+08.1f'

desc = ["CSCRNA",
        ["predict_corners", "predicted corners flag", 1, str],
        ["ulcnr_lat", "lat UL", 9, float, {'frmt': _lat_frmt}],
        ["ulcnr_long", "long UL", 10, float, {'frmt': _long_frmt}],
        ["ulcnr_ht", "height UL", 8, float, {'frmt': _ht_frmt}],
        ["urcnr_lat", "lat UR", 9, float, {'frmt': _lat_frmt}],
        ["urcnr_long", "long UR", 10, float, {'frmt': _long_frmt}],
        ["urcnr_ht", "height UR", 8, float, {'frmt': _ht_frmt}],
        ["lrcnr_lat", "lat LR", 9, float, {'frmt': _lat_frmt}],
        ["lrcnr_long", "long LR", 10, float, {'frmt': _long_frmt}],
        ["lrcnr_ht", "height LR", 8, float, {'frmt': _ht_frmt}],
        ["llcnr_lat", "lat LL", 9, float, {'frmt': _lat_frmt}],
        ["llcnr_long", "long LL", 10, float, {'frmt': _long_frmt}],
        ["llcnr_ht", "height LL", 8, float, {'frmt': _ht_frmt}],
]

TreCSCRNA = create_nitf_tre_structure("TreCSCRNA",desc,hlp=hlp)

