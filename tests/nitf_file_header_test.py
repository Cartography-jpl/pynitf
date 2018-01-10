from pynitf.nitf_file_header import *
from pynitf_test_support import *
import io, six

def test_basic():
    t = NitfFileHeader()
    with open(unit_test_data + "sample.ntf", 'rb') as fh:
        t.read_from_file(fh)
    assert t.fhdr == "NITF"
    assert t.fver == "02.10"
    assert t.clevel == 3
    assert t.stype == "BF01"
    assert t.ostaid == "GDAL"
    assert t.fdt == "20021216151629"
    assert t.fsclas == "U"
    assert t.fscop == 0
    assert t.fscpys == 0
    assert t.encryp == 0
    assert t.fbkgc == b'\x00\x00\x00'
    assert t.fl == 943
    assert t.hl == 404
    assert t.numi == 1
    assert list(t.lish) == [439]
    assert list(t.li) == [100]
    assert t.nums == 0
    assert t.numt == 0
    assert t.numdes == 0
    assert t.udhdl == 0
    if(False):
        print(t)

def test_write():
    t = NitfFileHeader()
    fh = six.BytesIO()
    t.write_to_file(fh)
    # We manually check the results of this file header as valid by using
    # show_nitf++ from nitro and gdalinfo from GDAL. For a simple automated
    # test, we just make sure that we back the same byte string as we previously
    # checked.
    if(False):
        with open("y.ntf", "wb") as fh:
            t.write_to_file(fh)
    assert fh.getvalue() == b'NITF02.1003BF01          20021216151629                                                                                U                                                                                                                                                                      00000000000\x00\x00\x00                                          0000000000000000000000000000000000000000000000'

        
