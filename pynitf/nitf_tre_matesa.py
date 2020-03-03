from .nitf_field import StringFieldData
from .nitf_tre import Tre, tre_tag_to_cls
import io

hlp = '''This is the MATESA TRE, Mates.

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (STDI-0002 V4.0, available at
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

MATESA v1.0 final v4 2019-02-12.
'''

desc = [["cur_source", "Current File/Segment Source", 42, str],
        ["cur_mate_type", "Current File/Segment Mate Type", 16, str],
        ["cur_file_id_len", "Length of CUR FILE ID field", 4, int],
        ["cur_file_id", "ID of the Current File/Segment", "f.cur_file_id_len", None,
          {'field_value_class' : StringFieldData}],
        ["num_groups", "Number of Mate Relationship Types", 4, int],
        [["loop", "f.num_groups"],
         ["relationship", "Mate Relationship", 24, str],
         ["num_mates", "Number of Mates", 4, int],
         [["loop", "f.num_mates[i1]"],
          ["source", "Mate Source", 42, str],
          ["mate_type", "Identifier Type", 16, str],
          ["mate_id_len", "Length of the mth MATE IDnm field", 4, int],
          ["mate_id", "Mate File Identifier","f.mate_id_len[i1, i2]", None,
           {'field_value_class' : StringFieldData}],
          ],
        ],
]

class TreMATESA(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "MATESA"
    def summary(self):
        res = io.StringIO()
        print("TRE - MATESA num_groups:%d" % (self.num_groups), file=res)
        return res.getvalue()

tre_tag_to_cls.add_cls(TreMATESA)    

__all__ = [ "TreMATESA" ]
