from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the MIMCSA TRE, Motion Imagery Collection Summary.

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (NGA.STND.0044_1.3_MIE4NITF Adjudicated v3.pdf), 
available at https://nsgreg.nga.mil/doc/view?i=4754

MIMCSA is documented in Table 11.
'''
desc = ["MIMCSA",
        ["layer_id", "Layer ID", 36, str],
        ["nominal_frame_rate", "Nominal Frame Rate", 13, float],
        ["min_frame_rate", "Minimum Frame Rate", 13, float],
        ["max_frame_rate", "Maximum Frame Rate", 13, float],
        ["t_rset", "Temporal Resolution Set", 2, int],
        ["mi_req_decoder", "Image Compression", 2, str, {'default' : 'NC'}],
        ["mi_req_profile", "Compression Profile", 36, str],
        ["mi_req_level", "Compression Level", 6, str],
]

TreMIMCSA = create_nitf_tre_structure("TreMIMCSA",desc,hlp=hlp)

def _summary(self):
    res = six.StringIO()
    print("MIMCSA:", file=res)
    print("Layer ID: %s" % (self.layer_id), file=res)
    print("Nominal Frame Rate: %f" % (self.nominal_frame_rate), file=res)
    print("Minimum Frame Rate: %f" % (self.min_frame_rate), file=res)
    print("Maximum Frame Rate: %f" % (self.max_frame_rate), file=res)
    print("Temporal Resolution Set: %d" % (self.t_rset), file=res)
    print("Image Compression: %s" % (self.mi_req_decoder), file=res)
    print("Compression Profile: %s" % (self.mi_req_profile), file=res)
    print("Compression Level: %s" % (self.mi_req_level), file=res)
    return res.getvalue()

TreMIMCSA.summary = _summary

__all__ = [ "TreMIMCSA" ]
