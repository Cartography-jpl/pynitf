from __future__ import print_function
from .nitf_field import *
from .nitf_des import *
from .nitf_des_csattb import udsh
import six

hlp = '''This is a NITF CSSFAB DES. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in a separate DRAFT document for the SNIP standard.
'''

_quat_format = "%+18.15lf"

desc2 =["CSSFAB",
        ['sensor_type', 'Sensor Type', 1, str],
        ['band_type', 'Spectral Band Category', 1, str],
        ['band_wavelength', 'Reference wavelength', 11, float,
         {'frmt': '%02.8lf'}],
        ['n_bands', "Number bands", 5, int, {'frmt' : '%05d'}],
        [["loop","f.n_bands"],
         ["band_index", "Band Order Index of the nth Spectral Band of the Associated Image Segments", 5, int, {'frmt' : '%05d'}],
         ["irepband", "Band-Specific Representation of the nth Band of the Associated Image Segments", 2, str],
         ["isubcat", "Band-Specific Sub-Category of the nth Band of the Associated Image Segments", 6, str],
         ],
        ['num_fl_pts', "Number of Focal Length Points", 3, int, {'frmt' : '%03d'}],
        # More
       ]

#print (desc2)

# udsh here is a from nitf_des_csattb, since the same user defined subheader
# is used for both
(DesCSSFAB, DesCSSFAB_UH) = create_nitf_des_structure("DesCSSFAB", desc2, udsh, hlp=hlp, data_after_allowed=True)
# Temp data_after_allowed

DesCSSFAB.desid = hardcoded_value("CSSFAB")
DesCSSFAB.desver = hardcoded_value("01")

def _summary(self):
    res = six.StringIO()
    print("CSSFAB", file=res)
    return res.getvalue()

DesCSSFAB.summary = _summary

register_des_class(DesCSSFAB)
__all__ = ["DesCSSFAB", "DesCSSFAB_UH"]
