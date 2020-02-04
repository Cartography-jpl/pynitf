from pynitf.nitf_tre import *
from pynitf.nitf_tre_rsmapa import *
from pynitf_test_support import *
import io

def test_tre_rsmapa():
    t = TreRSMAPA()
    t.iid = 'abc'
    t.edition = 'abc'
    t.tid = 'cde'
    t.npar = 36
    t.xuol = 0.1234567890
    t.yuol = 0.1234567890
    t.zuol = 0.1234567890
    t.xuxl = 0.1234567890
    t.xuyl = 0.1234567890
    t.xuzl = 0.1234567890
    t.yuxl = 0.1234567890
    t.yuyl = 0.1234567890
    t.yuzl = 0.1234567890
    t.zuxl = 0.1234567890
    t.zuyl = 0.1234567890
    t.zuzl = 0.1234567890
    t.ir0 = 1
    t.irx = 1
    t.iry = 1
    t.irz = 1
    t.irxx = 1
    t.irxy = 1
    t.irxz = 1
    t.iryy = 1
    t.iryz = 1
    t.irzz = 1
    t.ic0 = 1
    t.icx = 1
    t.icy = 1
    t.icz = 1
    t.icxx = 1
    t.icxy = 1
    t.icxz = 1
    t.icyy = 1
    t.icyz = 1
    t.iczz = 1
    t.gx0 = 1
    t.gy0 = 1
    t.gz0 = 1
    t.gxr = 1
    t.gyr = 1
    t.gzr = 1
    t.gs = 1
    t.gxx = 1
    t.gxy = 1
    t.gxz = 1
    t.gyx = 1
    t.gyy = 1
    t.gyz = 1
    t.gzx = 1
    t.gzy = 1
    t.gzz = 1
    for a in range (t.npar):
        t.parval[a] = 0.01*a

    fh = io.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())

    assert fh.getvalue() == b'RSMAPA01242abc                                                                             abc                                     cde                                     36 1.23456789000000E-01 1.23456789000000E-01 1.23456789000000E-01 1.23456789000000E-01 1.23456789000000E-01 1.23456789000000E-01 1.23456789000000E-01 1.23456789000000E-01 1.23456789000000E-01 1.23456789000000E-01 1.23456789000000E-01 1.23456789000000E-01010101010101010101010101010101010101010101010101010101010101010101010101 0.00000000000000E+00 1.00000000000000E-02 2.00000000000000E-02 3.00000000000000E-02 4.00000000000000E-02 5.00000000000000E-02 6.00000000000000E-02 7.00000000000000E-02 8.00000000000000E-02 9.00000000000000E-02 1.00000000000000E-01 1.10000000000000E-01 1.20000000000000E-01 1.30000000000000E-01 1.40000000000000E-01 1.50000000000000E-01 1.60000000000000E-01 1.70000000000000E-01 1.80000000000000E-01 1.90000000000000E-01 2.00000000000000E-01 2.10000000000000E-01 2.20000000000000E-01 2.30000000000000E-01 2.40000000000000E-01 2.50000000000000E-01 2.60000000000000E-01 2.70000000000000E-01 2.80000000000000E-01 2.90000000000000E-01 3.00000000000000E-01 3.10000000000000E-01 3.20000000000000E-01 3.30000000000000E-01 3.40000000000000E-01 3.50000000000000E-01'
    fh2 = io.BytesIO(fh.getvalue())
    t2 = TreRSMAPA()
    t2.read_from_file(fh2)
    assert t.iid == 'abc'
    assert t.edition == 'abc'
    assert t.tid == 'cde'
    assert t.npar == 36
    assert t.xuol == 0.1234567890
    assert t.yuol == 0.1234567890
    assert t.zuol == 0.1234567890
    assert t.xuxl == 0.1234567890
    assert t.xuyl == 0.1234567890
    assert t.xuzl == 0.1234567890
    assert t.yuxl == 0.1234567890
    assert t.yuyl == 0.1234567890
    assert t.yuzl == 0.1234567890
    assert t.zuxl == 0.1234567890
    assert t.zuyl == 0.1234567890
    assert t.zuzl == 0.1234567890
    assert t.ir0 == 1
    assert t.irx == 1
    assert t.iry == 1
    assert t.irz == 1
    assert t.irxx == 1
    assert t.irxy == 1
    assert t.irxz == 1
    assert t.iryy == 1
    assert t.iryz == 1
    assert t.irzz == 1
    assert t.ic0 ==1
    assert t.icx == 1
    assert t.icy == 1
    assert t.icz == 1
    assert t.icxx == 1
    assert t.icxy == 1
    assert t.icxz == 1
    assert t.icyy == 1
    assert t.icyz == 1
    assert t.iczz == 1
    assert t.gx0 == 1
    assert t.gy0 == 1
    assert t.gz0 == 1
    assert t.gxr == 1
    assert t.gyr == 1
    assert t.gzr == 1
    assert t.gs == 1
    assert t.gxx == 1
    assert t.gxy == 1
    assert t.gxz == 1
    assert t.gyx == 1
    assert t.gyy == 1
    assert t.gyz == 1
    assert t.gzx == 1
    assert t.gzy == 1
    assert t.gzz == 1
    for a in range(t.npar):
        assert t.parval[a] == 0.01 * a

# Tests for other parts
