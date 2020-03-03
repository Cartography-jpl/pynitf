from .nitf_tre import Tre, tre_tag_to_cls
import io

hlp = '''This is the TMINTA TRE, Time Interval Definition

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (NGA.STND.0044_1.3_MIE4NITF Adjudicated v3.pdf), 
available at https://nsgreg.nga.mil/doc/view?i=4754

TMINTA is documented in Table 14.
'''
desc = [["num_time_int", "Number of Time Intervals", 4, int],
        [["loop", "f.num_time_int"],
         ["time_interval_index", "Time Interval Index", 6, int],
         ["start_timestamp", "Time Interval Start Time", 24, str],
         ["end_timestamp", "Time Interval End Time", 24, str],
         ],
]

class TreTMINTA(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "TMINTA"

tre_tag_to_cls.add_cls(TreTMINTA)    

__all__ = [ "TreTMINTA" ]
