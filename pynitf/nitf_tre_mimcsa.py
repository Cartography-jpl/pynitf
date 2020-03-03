from .nitf_tre import Tre, tre_tag_to_cls
import io

hlp = '''This is the MIMCSA TRE, Motion Imagery Collection Summary.

The field names can be pretty cryptic, but are documented in detail in
the NITF TRE documentation (NGA.STND.0044_1.3_MIE4NITF Adjudicated v3.pdf), 
available at https://nsgreg.nga.mil/doc/view?i=4754

MIMCSA is documented in Table 11.
'''
desc = [["layer_id", "Layer ID", 36, str],
        ["nominal_frame_rate", "Nominal Frame Rate", 13, float],
        ["min_frame_rate", "Minimum Frame Rate", 13, float],
        ["max_frame_rate", "Maximum Frame Rate", 13, float],
        ["t_rset", "Temporal Resolution Set", 2, int],
        ["mi_req_decoder", "Image Compression", 2, str, {'default' : 'NC'}],
        ["mi_req_profile", "Compression Profile", 36, str],
        ["mi_req_level", "Compression Level", 6, str],
]


class TreMIMCSA(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "MIMCSA"

tre_tag_to_cls.add_cls(TreMIMCSA)    

__all__ = [ "TreMIMCSA" ]
