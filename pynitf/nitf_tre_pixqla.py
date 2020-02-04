from .nitf_field import *
from .nitf_tre import *
import io

hlp = '''This is the PIXQLA TRE, Pixel Quality.

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (STDI-0002 V4.0, available at
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for
where in the document a particular TRE is defined.

PIXQLA is documented at AA-14.
'''
desc = ["PIXQLA",
        ["numais", "Number of Associated Image Segments", 3, str],
        [["loop", "0 if f.numais == 'ALL' else int(f.numais)"],
         ["aisdlvl", "Associated Image Segment Display Level", 3, int]],
        ["npixqual", "Number of Pixel Quality Conditions", 4, int],
        ["pq_bit_value", "Pixel Quality Bit Value", 1, str],
        [["loop", "f.npixqual"],
         ["pq_condition", "Pixel Quality Condition", 40, str]],
]

TrePIXQLA = create_nitf_tre_structure("TrePIXQLA",desc,hlp=hlp)
# This value is always "1", that is the only allowed value for it
TrePIXQLA.pq_bit_value_value = hardcoded_value("1")

def _summary(self):
    res = io.StringIO()
    print("PIXQLA %s Associated ISs, %d Quality Conditions" % (self.numais, self.npixqual), file=res)
    return res.getvalue()

TrePIXQLA.summary = _summary

__all__ = ["TrePIXQLA" ]
