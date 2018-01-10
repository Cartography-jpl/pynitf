from pynitf.nitf_tre import *
from pynitf.nitf_tre_csde import *
from pynitf.nitf_file_header import *
from pynitf.nitf_image_subheader import *
from test_support import *
import io, six

def test_tre():
    # This is part of USE00A, but we give it a different name so it
    # doesn't conflict with the real TRE defined in nitf_tre_csde.py
    TestUSE00A = create_nitf_tre_structure("TestUSE00A",
        ["USETST",
         ["angle_to_north", "Angle to North", 3, int],
         ["mean_gsd", "Mean GSD", 5, float, {"frmt" : "%05.1lf"}],
         [None, None, 1, str],
         ["dynamic_range", "Dynamic Range", 5, int],
         ])
    t = TestUSE00A()
    t.angle_to_north = 270
    t.mean_gsd = 105.2
    t.dynamic_range = 2047
    fh = six.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'USETST00014270105.2 02047'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TestUSE00A()
    t2.read_from_file(fh2)
    assert t2.angle_to_north == 270
    assert_almost_equal(t2.mean_gsd, 105.2)
    assert t.dynamic_range == 2047
    
def test_tre_read():
    '''Read a file that has a TRE in it'''
    t = NitfFileHeader()
    t2 = NitfImageSubheader()
    with open(unit_test_data + "test_use00a.ntf", 'rb') as fh:
        t.read_from_file(fh)
        t2.read_from_file(fh)
    trelist = read_tre_data(t2.ixshd)
    assert(len(trelist) == 1)
    t = trelist[0]
    assert t.angle_to_north == 270
    assert_almost_equal(t.mean_gsd, 105.2)
    assert t.dynamic_range == 2047
    assert_almost_equal(t.obl_ang, 34.12)
    assert_almost_equal(t.roll_ang, -21.15)
    assert t.n_ref == 0
    assert t.rev_num == 3317
    assert t.n_seg == 1
    assert t.max_lp_seg == 6287
    assert_almost_equal(t.sun_el, 68.5)
    assert_almost_equal(t.sun_az, 131.3)
    

