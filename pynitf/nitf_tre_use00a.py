from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the USE00A TRE, Exploitation Useability.

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (STDI-0002 V4.0, available at
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).
'''

desc = ["USE00A",
        ["angle_to_north", "Angle to North", 3, int],
        ["mean_gsd", "Mean Ground Sample Distance", 5, float, {'frmt': "%05.1lf"}],
        ["reserved1", "Reserved 1", 1, str],
        ["dynamic_range", "Dynamic Range", 5, int],
        ["reserved2", "Reserved 2", 3, str],
        ["reserved3", "Reserved 3", 1, str],
        ["reserved4", "Reserved 4", 3, str],
        ["obl_ang", "Obliquity Angle", 5, float, {'frmt': "%05.2lf"}],
        ["roll_ang", "Roll Angle", 6, float, {'frmt': "%+06.2lf"}],
        ["reserved5", "Reserved 5", 12, str],
        ["reserved6", "Reserved 6", 15, str],
        ["reserved7", "Reserved 7", 4, str],
        ["reserved8", "Reserved 8", 1, str],
        ["reserved9", "Reserved 9", 3, str],
        ["reserved10", "Reserved 10", 1, str],
        ["reserved11", "Reserved 11", 1, str],
        ["n_ref", "Number of Reference Lines", 2, int],
        ["rev_num", "Revolution Number", 5, int],
        ["n_seg", "Number of Segments", 3, int],
        ["max_lp_seg", "Maximum Lines Per Segment", 6, int],
        ["reserved12", "Reserved 12", 6, str],
        ["reserved13", "Reserved 13", 6, str],
        ["sun_el", "Sun Elevation", 5, float, {'frmt': "%05.1lf"}],
        ["sun_az", "Sun Azimuth", 5, float, {'frmt':"%05.1lf"}]
]

TreUSE00A = create_nitf_tre_structure("TreUSE00A",desc,hlp=hlp)

def _summary(self):
    res = six.StringIO()
    print("USE00A Angle to North %d, Number of Segments: %d" % (self.angle_to_north, self.n_seg), file=res)
    return res.getvalue()

TreUSE00A.summary = _summary

__all__ = [ "TreUSE00A" ]
