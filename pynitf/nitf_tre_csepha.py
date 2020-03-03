from .nitf_tre import Tre, tre_tag_to_cls
import io

hlp = '''This is the CSEPHA TRE, Ephemeris Data. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0006, available at 
www.gwg.nga.mil/ntb/baseline/docs/stdi0006/NCDRD_20Dec06.pdf).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

CSEPHA is documented in section 3.4.
'''
desc = [["ephem_flag", "ephemeris flag", 12, str],
        ["dt_ephem", "time b/w eph vectors", 5, float, {"frmt" : "%03.1lf"}],
        ["date_ephem", "day of first eph vector", 8, int],
        ["t0_ephem", "UTC of first eph vector", 13, str],
        ["num_ephem", "number of eph vectors", 3, int],
        [["loop", "f.num_ephem"],
         ["ephem_x", "x-coor of eph vector", 12, float, {"frmt" : "%+012.2lf"}],
         ["ephem_y", "y-coor of eph vector", 12, float, {"frmt" : "%+012.2lf"}],
         ["ephem_z", "z-coor of eph vector", 12, float, {"frmt" : "%+012.2lf"}],
        ], #end loop
]

class TreCSEPHA(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "CSEPHA"
    def summary(self):
        res = io.StringIO()
        print("TRE - CSEPHA: %s %d ephemeris vectors" %
              (self.ephem_flag, self.num_ephem), file=res)
        return res.getvalue()

tre_tag_to_cls.add_cls(TreCSEPHA)

__all__ = [ "TreCSEPHA", ]
