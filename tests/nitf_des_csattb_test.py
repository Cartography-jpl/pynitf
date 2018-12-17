from pynitf.nitf_des import *
from pynitf.nitf_des_csattb import *
from pynitf.nitf_file import NitfDesSegment
from pynitf_test_support import *
import io, six

def test_des_snip_user_header():

    ds = DesCSATTB_UH()
    ds.id = '4385ab47-f3ba-40b7-9520-13d6b7a7f311'
    ds.numais = '010'
    for i in range(int(ds.numais)):
        ds.aisdlvl[i] = 5 + i
    ds.reservedsubh_len = 0

    fh_ds = six.BytesIO()
    ds.write_to_file(fh_ds)
    print(fh_ds.getvalue())
    assert fh_ds.getvalue() == b'4385ab47-f3ba-40b7-9520-13d6b7a7f3110100050060070080090100110120130140000000'

    fh2_ds = six.BytesIO(fh_ds.getvalue())
    d2_ds = DesCSATTB_UH()
    d2_ds.read_from_file(fh2_ds)

    assert d2_ds.id == '4385ab47-f3ba-40b7-9520-13d6b7a7f311'
    assert d2_ds.numais == '010'
    for i in range(int(d2_ds.numais)):
        assert d2_ds.aisdlvl[i] == 5 + i
    assert d2_ds.reservedsubh_len == 0

def test_des_csattb_basic():

    d = DesCSATTB()

    d.qual_flag_att = 1
    d.interp_type_att = 1
    d.att_type = 1
    d.eci_ecf_att = 0
    d.dt_att = 900.5
    d.date_att = 20170501
    d.t0_att = 235959.100001000
    d.num_att = 5
    for n in range(d.num_att):
        d.q1[n] = -0.11111
        d.q2[n] = -0.11111
        d.q3[n] = 0.11111
        d.q4[n] = 0.11111
    d.reserved_len = 0

    fh = six.BytesIO()
    dseg = NitfDesSegment(des=d);
    hs, ds = dseg.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'DECSATTB                   01U                                                                                                                                                                      0046                                    0  00000001110900.50000000020170501235959.10000100000005-0.111110000000000-0.111110000000000+0.111110000000000+0.111110000000000-0.111110000000000-0.111110000000000+0.111110000000000+0.111110000000000-0.111110000000000-0.111110000000000+0.111110000000000+0.111110000000000-0.111110000000000-0.111110000000000+0.111110000000000+0.111110000000000-0.111110000000000-0.111110000000000+0.111110000000000+0.111110000000000000000000'

    fh2 = six.BytesIO(fh.getvalue())
    dseg2 = NitfDesSegment(header_size=hs, data_size=ds)
    dseg2.read_from_file(fh2)
    d2 = dseg2.des

    assert d2.qual_flag_att == 1
    assert d2.interp_type_att == 1
    assert d2.att_type == 1
    assert d2.eci_ecf_att == 0
    assert d2.dt_att == 900.5
    assert d2.date_att == 20170501
    assert d2.t0_att == 235959.100001000
    assert d2.num_att == 5
    for n in range(d2.num_att):
        assert d2.q1[n] == -0.11111
        assert d2.q2[n] == -0.11111
        assert d2.q3[n] == 0.11111
        assert d2.q4[n] == 0.11111
    assert d2.reserved_len == 0

    print (d2.summary())
