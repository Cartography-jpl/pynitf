from pynitf.nitf_tre import *
from pynitf.nitf_tre_illumb import *
from pynitf_test_support import *
import io, six

#@pytest.mark.skip
def test_tre_illumb_basic():
    t = TreILLUMB()

    # Set some values
    t.num_bands = 1
    t.band_unit = "Some band unit of measure"
    t.lbound[0] = 17.0
    t.ubound[0] = 42.0
    t.num_others = 0
    t.num_coms = 1
    t.comment[0] = "Blah blah blah"
    t.existence_mask = 0x000000
    t.num_illum_sets = 1
    t.datetime[0] = "Today"
    t.target_lat[0] = 35.0
    t.target_lon[0] = -130.0
    t.target_hgt[0] = 1000.0

    fh = six.BytesIO()
    t.write_to_file(fh)
    foo
    print('getvalue returns:', fh.getvalue())
    assert fh.getvalue() == b'CSCRNA00109Y-90.00000-170.00000+10555.5+09.00000-170.00000+00000.0+90.00000+170.00000+00004.5-09.00000+017.00000-00555.5'

    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreILLUMB()
    t2.read_from_file(fh2)
    assert t2.predict_corners == "Y"

    print (t2.summary())
