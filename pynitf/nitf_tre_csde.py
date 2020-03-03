from .nitf_tre import Tre, tre_tag_to_cls
import io

hlp = '''This is the STDIDC TRE, Standard ID

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002 V4.0, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

STDIDC is documented at D-8.

NOTE that "pass" is a python keyword. Therefore, the 3rd field is called "pass_"
'''
desc = [["acquisition_date", "Acquisition Date", 14, str],
        ["mission", "Mission", 14, str],
        ["pass_", "Pass", 2, str],
        ["op_num", "Op number", 3, int],
        ["start_segment", "Start segment", 2, str],
        ["repro_num", "Repro number", 2, int],
        ["replay_regen", "Replay regen", 3, str],
        ["blank_fill", "Blank fill", 1, str],
        ["start_column", "Start column", 3, int],
        ["start_row", "Start row", 5, int],
        ["end_segment", "End segment", 2, str],
        ["end_column", "End column", 3, int],
        ["end_row", "End row", 5, int],
        ["country", "Country", 2, str, {"optional" : True}],
        ["wac", "WAC", 4, int, {"optional" : True}],
        ["location", "Location", 11, str],
	[None, None, 5, None],
	[None, None, 8, None]
]

class TreSTDIDC(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "STDIDC"
    def summary(self):
        res = io.StringIO()
        print("TRE - STDIDC: %s, %s, %s, %d" %
              (self.acquisition_date, self.mission, self.pass_, self.op_num),
              file=res)
        return res.getvalue()

tre_tag_to_cls.add_cls(TreSTDIDC)    
    
hlp = '''This is the USE00A TRE, Exploitation Usability TRE. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002 V4.0, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

USE00A is documented at D-11.
'''
desc = [["angle_to_north", "Angle to North", 3, int],
        ["mean_gsd", "Mean GSD", 5, float, {"frmt" : "%05.1lf"}],
        [None, None, 1, str],
        ["dynamic_range", "Dynamic Range", 5, int, {"optional" : True}],
        [None, None, 3, str],
        [None, None, 1, str],
        [None, None, 3, str],
        ["obl_ang", "Obliquity Angle", 5, float, {"frmt" : "%05.2lf",
                                                  "optional" :True}],
        ["roll_ang", "Roll Angle", 6, float, {"frmt" : "%+04.2lf",
                                              "optional" : True}],
        [None, None, 12, str],
        [None, None, 15, str],
        [None, None, 4, str],
        [None, None, 1, str],
        [None, None, 3, str],
        [None, None, 1, str],
        [None, None, 1, str],
        ["n_ref", "Number of Reference Lines", 2, int],
        ["rev_num", "Revolution Number", 5, int],
        ["n_seg", "Number of Segments", 3, int],
        ["max_lp_seg", "Max Lines per Segment", 6, int, {"optional" : True}],
        [None, None, 6, str],
        [None, None, 6, str],
        ["sun_el", "Sun Elevation", 5, float, {"frmt" : "%+05.1lf"}],
        ["sun_az", "Sun Azimuth", 5, float, {"frmt" : "%05.1lf"}],
]

class TreUSE00A(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "USE00A"

tre_tag_to_cls.add_cls(TreUSE00A)    

__all__ = ["TreSTDIDC", "TreUSE00A"]
