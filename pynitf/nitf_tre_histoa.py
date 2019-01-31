from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the HISTOA TRE, History version A.

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (STDI-0002 V4.0, available at
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for
where in the document a particular TRE is defined.

HISTOA is documented at L-10.
'''
desc = ["HISTOA",
        ["systype", "System Type", 20, str],
        ["pc", "Prior Compression", 12, str],
        ["pe", "Prior Enhancements", 4, str],
        ["remap_flag", "System Specific Remap", 1, str],
        ["lutid", "Data Mapping ID from the ESD", 2, int],
        ["nevents", "Number of Processing Events", 2, int],
        [["loop", "f.nevents"],
         ["pdate", "Processing Date And Time", 14, str],
         ["psite", "Processing Site", 10, str],
         ["pas", "Softcopy Processing Application", 10, str],
         ["nipcom", "Number of Image Processing Comments", 1, int],
         [["loop", "f.nipcom[i1]"],
          ["ipcom", "Image Processing Comment", 80, str]],
         ["ibpp", "Input Bit Depth (actual)", 2, int],
         ["ipvtype", "Input Pixel Value Type", 3, str],
         ["inbwc", "Input Bandwidth Compression", 10, str],
         ["disp_flag", "Display-Ready Flag", 1, int, {'optional' : True}],
         ["rot_flag", "Image Rotation", 1, int],
         ["rot_angle", "Angle Rotation", 8, float, {'condition' : "f.rot_flag[i1] == 1"}],
         ["asym_flag", "Asymmetric Correction", 1, str],
         ["zoomrow", "Mag in Line (row) Direction", 7, float, {'condition' : "f.asym_flag[i1] == '1'"}],
         ["zoomcol", "Mag in Element (column) Direction", 7, float, {'condition' : "f.asym_flag[i1] == '1'"}],
         ["proj_flag", "Image Projection", 1, str],
         ["sharp_flag", "Sharpening", 1, int],
         ["sharpfam", "Sharpening Family Number", 2, int, {'condition' : "f.sharp_flag[i1] == 1"}],
         ["sharpmem", "Sharpening Member Number", 2, int, {'condition' : "f.sharp_flag[i1] == 1"}],
         ["mag_flag", "Symmetrical Magnification", 1, int],
         ["mag_level", "Level of Relative Magnification", 7, float, {'condition' : "f.mag_flag[i1] == 1"}],
         ["dra_flag", "Dynamic Range Adjustment (DRA)", 1, int],
         ["dra_mult", "DRA Multiplier", 7, float, {'condition' : "f.dra_flag[i1] == 1"}],
         ["dra_sub", "DRA Subtractor", 5, int, {'condition' : "f.dra_flag[i1] == 1"}],
         ["ttc_flag", "Tonal Transfer Curve (TTC)", 1, int],
         ["ttcfam", "TTC Family Number", 2, int, {'condition' : "f.ttc_flag[i1] == 1"}],
         ["ttcmem", "TTC Member Number", 2, int, {'condition' : "f.ttc_flag[i1] == 1"}],
         ["devlut_flag", "Device LUT", 1, int],
         ["obpp", "Output Bit Depth (actual)", 2, int],
         ["opvtype", "Output Pixel Value Type", 3, str],
         ["outbwc", "Output Bandwidth Compression", 10, str],
        ], # End nevents loop
]

TreHISTOA = create_nitf_tre_structure("TreHISTOA",desc,hlp=hlp)

def _summary(self):
    res = six.StringIO()
    print("HISTOA: %d events:" % (self.nevents), file=res)
    for i in range(self.nevents):
        for j in range(self.nipcom[i]):
            print("%d.%d: %s" % (i, j, self.ipcom[i, j]), file=res)
    return res.getvalue()

TreHISTOA.summary = _summary

__all__ = [ "TreHISTOA" ]
