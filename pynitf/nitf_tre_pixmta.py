from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *

hlp = '''This is the PIXMTA TRE, Pixel Metric.

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (STDI-0002 V4.0, available at
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

PIXMTA is currently, Dec 2017, defined in the SNIP draft document.
It will be finalized in sometime 2018
'''

_origin_format = "%+14.7E"
_coef_format = "%+15.8E"

desc = ["PIXMTA",
        ["numais", "Number of Associated Image Segments", 3, str],
        [["loop", "0 if f.numais == 'ALL' else int(f.numais)"],
         ["aisdlvl", "Associated Image Segment Display Level", 3, int]],
        ["origin_x", "Column Position of the Upper Left Pixel Metric Value", 14, float, {'frmt': _origin_format}],
        ["origin_y", "Row Position of the Upper Left Pixel Metric Value", 14, float, {'frmt': _origin_format}],
        ["scale_x", "Column-Based Scale Factor", 14, float, {'frmt': _origin_format}],
        ["scale_y", "Row-Based Scale Factor", 14, float, {'frmt': _origin_format}],
        ["sample_mode", "Pixel Metric Sampling Mode", 1, str],
        ["nummetrics", "Number of Metrics Specified in the Pixel Metric Image Segment", 5, int],
        ["perband", "Per Band Metric Flag", 1, str],
        [["loop", "f.nummetrics"],
         ["description", "Description of the mth Pixel Metric", 40, str],
         ["unit", "Unit Measure for the mth Pixel Metric", 40, str],
         ["fittype", "Mathematical Form of the Data Transformation for the mth Pixel Metric", 1, str],
         ["numcoef", "Number of Coefficients Used by the Data Transformation of the mth Pixel Metric", 1, int,
          {'condition': "f.fittype[i1] == 'P'"}],
          [["loop", "0 if f.fittype[i1] == 'D' else int(f.numcoef[i1])"],
           ["coef", "jth Data Transformation Coefficient for the mth Pixel Metric", 15, float, {'frmt': _coef_format}]]],
        ["reserved_len", "Size of the Reserved Field", 5, int],
        ["reserved", "Reserved Data Field", "f.reserved_len", None, {'field_value_class' : FieldData}]
]

TrePIXMTA = create_nitf_tre_structure("TrePIXMTA",desc,hlp=hlp)

def _summary(self):
    res = six.StringIO()
    print("PIXMTA %s Associated ISs, %d Metrics" % (self.numais, self.nummetrics), file=res)
    return res.getvalue()

TrePIXMTA.summary = _summary
