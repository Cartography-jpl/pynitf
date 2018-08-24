from pynitf.nitf_tre import *
from pynitf.nitf_tre_cscrna import *
from pynitf_test_support import *
import io, six

def test_tre_cscrna_basic():

    t = TreCSCRNA()

    # Set some values
    t.predict_corners = "Y"
    t.ulcnr_lat = -90.00000
    t.ulcnr_long = -170.00000
    t.ulcnr_ht = 10555.5
    t.urcnr_lat = 9.00000
    t.urcnr_long = -170.00000
    t.urcnr_ht = 0
    t.lrcnr_lat = 90.00000
    t.lrcnr_long = 170.00000
    t.lrcnr_ht = 4.5
    t.llcnr_lat = -9.00000
    t.llcnr_long = 17.00000
    t.llcnr_ht = -555.5

    fh = six.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'CSCRNA00109Y-90.00000-170.00000+10555.5+09.00000-170.00000+00000.0+90.00000+170.00000+00004.5-09.00000+017.00000-00555.5'

    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreCSCRNA()
    t2.read_from_file(fh2)
    assert t2.predict_corners == "Y"
    assert t2.ulcnr_lat == -90.00000
    assert t.ulcnr_long == -170.00000
    assert t.ulcnr_ht == 10555.5
    assert t.urcnr_lat == 9.00000
    assert t.urcnr_long == -170.00000
    assert t.urcnr_ht == 0
    assert t.lrcnr_lat == 90.00000
    assert t.lrcnr_long == 170.00000
    assert t.lrcnr_ht == 4.5
    assert t.llcnr_lat == -9.00000
    assert t.llcnr_long == 17.00000
    assert t.llcnr_ht == -555.5

    print (t2.summary())
