from pynitf.nitf_tre import *
from pynitf.nitf_tre_mimcsa import *
from pynitf_test_support import *
import io, six
    
def test_tre_mimcsa_basic():

    t = TreMIMCSA()

    #Set some values
    t.layer_id = "Some layer ID"
    t.nominal_frame_rate = 22.2
    t.min_frame_rate = 10.1
    t.max_frame_rate = 29.9
    t.t_rset = 0
    t.mi_req_decoder = "NC"
    t.mi_req_profile = "N/A"
    t.mi_req_level = "N/A"

    print (t.summary())

    fh = six.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'MIMCSA00121Some layer ID                       22.200000000010.100000000029.900000000000NCN/A                                 N/A   '
