from pynitf.nitf_file_header import *
from pynitf.nitf_image_subheader import *
from pynitf_test_support import *
import io,six

def test_basic():
    t = NitfFileHeader()
    t2 = NitfImageSubheader()
    with open(unit_test_data + "sample.ntf", 'rb') as fh:
        t.read_from_file(fh)
        t2.read_from_file(fh)
    assert t2.im == "IM"
    assert t2.iid1 == "Missing"
    assert t2.idatim == "20021216151629"
    assert t2.isclas == "U"
    assert t2.encryp == 0
    assert t2.isorce == "Unknown"
    assert t2.nrows == 10
    assert t2.ncols == 10
    assert t2.pvtype == "INT"
    assert t2.irep == "MONO"
    assert t2.icat == "VIS"
    assert t2.abpp == 8
    assert t2.pjust == "R"
    assert t2.nicom == 0
    assert t2.ic == "NC"
    assert t2.nbands == 1
    assert list(t2.irepband) == ["M"]
    assert t2.isync == 0
    assert t2.imode == "B"
    assert t2.nbpr == 1
    assert t2.nbpc == 1
    assert t2.nppbh == 10
    assert t2.nppbv == 10
    assert t2.nbpp == 8
    assert t2.idlvl == 1
    assert t2.ialvl == 0
    assert t2.iloc == "0000000000"
    assert t2.imag == "1.0"
    assert t2.udidl == 0
    assert t2.ixshdl == 0
    # check that we can write and read the same values again
    fh = six.BytesIO()
    t2.write_to_file(fh)
    t2 = NitfImageSubheader()
    fh2 = six.BytesIO(fh.getvalue())
    t2.read_from_file(fh2)
    assert t2.im == "IM"
    assert t2.iid1 == "Missing"
    assert t2.idatim == "20021216151629"
    assert t2.isclas == "U"
    assert t2.encryp == 0
    assert t2.isorce == "Unknown"
    assert t2.nrows == 10
    assert t2.ncols == 10
    assert t2.pvtype == "INT"
    assert t2.irep == "MONO"
    assert t2.icat == "VIS"
    assert t2.abpp == 8
    assert t2.pjust == "R"
    assert t2.nicom == 0
    assert t2.ic == "NC"
    assert t2.nbands == 1
    assert list(t2.irepband) == ["M"]
    assert t2.isync == 0
    assert t2.imode == "B"
    assert t2.nbpr == 1
    assert t2.nbpc == 1
    assert t2.nppbh == 10
    assert t2.nppbv == 10
    assert t2.nbpp == 8
    assert t2.idlvl == 1
    assert t2.ialvl == 0
    assert t2.iloc == "0000000000"
    assert t2.imag == "1.0"
    assert t2.udidl == 0
    assert t2.ixshdl == 0

    print("\n"+t2.summary())
    
    
