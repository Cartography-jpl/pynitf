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

def test_geolo_corner():
    t = NitfImageSubheader()
    t.geolo_corner = 'G', [[50 + 30 / 60.0 + 20 / (60 * 60),
                            40 + 50 / 60.0 + 30 / (60 * 60)],
                           [50 + 30 / 60.0 + 40 / (60 * 60),
                            40 + 50 / 60.0 + 30 / (60 * 60)],
                           [50 + 30 / 60.0 + 40 / (60 * 60),
                            40 + 50 / 60.0 + 40 / (60 * 60)],
                           [50 + 30 / 60.0 + 20 / (60 * 60),
                            40 + 50 / 60.0 + 40 / (60 * 60)]], None
    assert t.icords == "G"
    assert t.igeolo == "405030N0503020E405030N0503040E405040N0503040E405040N0503020E"
    print(t.igeolo)
    fh = six.BytesIO()
    t.write_to_file(fh)
    t2 = NitfImageSubheader()
    fh2 = six.BytesIO(fh.getvalue())
    t2.read_from_file(fh2)
    print(t2.geolo_corner)
    t.geolo_corner = 'D', [[50 + 30 / 60.0 + 20 / (60 * 60),
                            40 + 50 / 60.0 + 30 / (60 * 60)],
                           [50 + 30 / 60.0 + 40 / (60 * 60),
                            40 + 50 / 60.0 + 30 / (60 * 60)],
                           [50 + 30 / 60.0 + 40 / (60 * 60),
                            40 + 50 / 60.0 + 40 / (60 * 60)],
                           [50 + 30 / 60.0 + 20 / (60 * 60),
                            40 + 50 / 60.0 + 40 / (60 * 60)]], None
    assert t.icords == "D"
    assert t.igeolo == "+40.842+050.506+40.842+050.511+40.844+050.511+40.844+050.506"
    print(t.igeolo)
    fh = six.BytesIO()
    t.write_to_file(fh)
    t2 = NitfImageSubheader()
    fh2 = six.BytesIO(fh.getvalue())
    t2.read_from_file(fh2)
    print(t2.geolo_corner)
    
    
