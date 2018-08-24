from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the MATESA TRE, Mates.

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (STDI-0002 V4.0, available at
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

MATESA is currently, Dec 2017, defined in the SNIP draft document.
It will be finalized in sometime 2018
'''

desc = ["MATESA",
        ["num_groups", "Number of Mate Relationship Types", 2, int],
        [["loop", "f.num_groups"],
         ["relationship", "Mate Relationship Type", 32, str],
         ["num_mates", "Number of Mates", 3, int],
         [["loop", "f.num_mates[i1]"],
          ["source", "Mate Source", 42, str],
          ["id_type", "Identifier Type", 20, str],
          ["mate_id", "Mate File Identifier",256, str],
         ],
        ],
]

TreMATESA = create_nitf_tre_structure("TreMATESA",desc,hlp=hlp)

def _summary(self):
    res = six.StringIO()
    print("MATESA num_groups:%d" % (self.num_groups), file=res)
    return res.getvalue()

TreMATESA.summary = _summary

__all__ = [ "TreMATESA" ]
