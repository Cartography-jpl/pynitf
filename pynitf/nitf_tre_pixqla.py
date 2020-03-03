from .nitf_tre import Tre, tre_tag_to_cls
import io

hlp = '''This is the PIXQLA TRE, Pixel Quality.

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (STDI-0002 V4.0, available at
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for
where in the document a particular TRE is defined.

PIXQLA is documented at AA-14.
'''
desc = [["numais", "Number of Associated Image Segments", 3, str],
        [["loop", "0 if f.numais == 'ALL' else int(f.numais)"],
         ["aisdlvl", "Associated Image Segment Display Level", 3, int]],
        ["npixqual", "Number of Pixel Quality Conditions", 4, int],
        # This value is always "1", that is the only allowed value for it
        ["pq_bit_value", "Pixel Quality Bit Value", 1, str,
         {"default" : "1", "hardcoded_value" : True}],
        [["loop", "f.npixqual"],
         ["pq_condition", "Pixel Quality Condition", 40, str]],
]


class TrePIXQLA(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "PIXQLA"
    def summary(self):
        res = io.StringIO()
        print("TRE - PIXQLA %s Associated ISs, %d Quality Conditions" %
              (self.numais, self.npixqual), file=res)
        return res.getvalue()

tre_tag_to_cls.add_cls(TrePIXQLA)    

__all__ = ["TrePIXQLA" ]
