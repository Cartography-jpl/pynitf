from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the ENGRDA TRE, Engineering data.

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (STDI-0002 V4.0, available at
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for
where in the document a particular TRE is defined.

HISTOA is documented at N-9.
'''
desc = ["ENGRDA",
        ["resrc", "Unique Source System Name", 20, str],
        ["recnt", "Record entry count", 3, int],
        [["loop", "f.recnt"],
         ["engln", "Engineering Data Label Length", 2, int],
         ["englbl", "Engineering Data Label", "f.engln[i1]", None,
          {'field_value_class' : StringFieldData}],
         ["engmtxc", "Engineering Matrix Data Column Count", 4, int],
         ["engmtxr", "Engineering Matrix Data Row Count", 4, int],
         ["engtyp", "Value Type of Engineering Data Element", 1, str],
         ["engdts", "Engineering Data Element Size", 1, int],
         ["engdatu", "Engineering Data Units", 2, str],
         ["engdatc", "Engineering Data Count", 8, int],
         ["engdata", "Engineering Data", "f.engdatc[i1]*f.engdts[i1]", None,
          {'field_value_class' : FieldData, 'size_not_updated' : True}],
        ], # End recnt loop
]

TreENGRDA = create_nitf_tre_structure("TreENGRDA",desc,hlp=hlp)
# engdatc isn't really a free variable, it is defined by the value of
# engmtxc and engmtxr
#def _f(self, key):
#TreENGRDA.engdatc_value = 
# We have rename engdata to engdataraw in the tre, and we then give a
# numpy interface to engdata

def _summary(self):
    res = six.StringIO()
    print("ENGRDA %s: %d Entries:" \
          % (self.resrc, self.recnt), file=res)
    for i in range(self.recnt):
        print("%d. %s [%d X %d] %s%d" \
              % (i, self.englbl[i], self.engmtxc[i], self.engmtxr[i], self.engtyp[i], self.engdts[i]), file=res)
    return res.getvalue()

TreENGRDA.summary = _summary

__all__ = [ "TreENGRDA" ]
