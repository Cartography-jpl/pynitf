from pynitf.nitf_tre import *
from pynitf.nitf_tre_use00a import *
from pynitf_test_support import *
import io, six

def test_tre_use00a():
    '''Basic test of use00a'''
    t = TreUSE00A()
    t.angle_to_north = 100
    t.mean_gsd = 111.2
    t.dynamic_range = 10000
    t.obl_ang = 30.5
    t.roll_ang = -30.5
    t.n_ref = 10
    t.rev_num = 10000
    t.n_seg = 2
    t.max_lp_seg = 900000
    t.sun_el = -45.2
    t.sun_az = 123.4
    fh = six.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'USE00A00107100111.2 10000       30.50-30.50                                     1010000002900000            -45.2123.4'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreUSE00A()
    t2.read_from_file(fh2)
    assert t2.angle_to_north == 100
    assert t2.mean_gsd == 111.2
    assert t2.dynamic_range == 10000
    assert t2.obl_ang == 30.5
    assert t2.roll_ang == -30.5
    assert t2.n_ref == 10
    assert t2.rev_num == 10000
    assert t2.n_seg == 2
    assert t2.max_lp_seg == 900000
    assert t.sun_el == -45.2
    assert t.sun_az == 123.4

    print(t2.summary())