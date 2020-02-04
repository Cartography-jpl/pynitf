from pynitf.nitf_tre import *
from pynitf.nitf_tre_illumb import *
from pynitf_test_support import *
import io

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

    fh = io.BytesIO()
    t.write_to_file(fh)
    print('getvalue returns:', fh.getvalue())
    assert fh.getvalue() == b'ILLUMB004650001Some band unit of measure                   1.700000E+01    4.200000E+01001Blah blah blah                                                                  World Geodetic System 1984                                                      WGE World Geodetic System 1984                                                      WE Geodetic                                                                        GEOD\x00\x00\x00001Today         +35.000000-130.000000 +1.000000E+03'

    fh2 = io.BytesIO(fh.getvalue())
    t2 = TreILLUMB()
    t2.read_from_file(fh2)

    print (t2.summary())
