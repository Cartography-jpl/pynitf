from pynitf.nitf_tre import *
from pynitf.nitf_tre_rsmida import *
from test_support import *
import io, six

def test_tre_rsmida():
    t = TreRSMIDA()
    t.iid = 'abc'
    t.edition = 'abc'
    t.isid = 'abc'
    t.sid = 'abc'
    t.stid = 'abc'
    t.year = 2017
    t.month=12
    t.day = 1
    t.hour = 10
    t.minute = 59
    t.second = 12.5
    t.grndd = 'G'
    t.xuor = 1234.567890
    t.yuor = 1234.567890
    t.zuor = 1234.567890
    t.xuxr = 0.1234567890
    t.xuyr = 0.1234567890
    t.xuzr = 0.1234567890
    t.yuxr = 0.1234567890
    t.yuyr = 0.1234567890
    t.yuzr = 0.1234567890
    t.zuxr = 0.1234567890
    t.zuyr = 0.1234567890
    t.zuzr = 0.1234567890
    t.v1x = 0.1234567890
    t.v1y = 0.1234567890
    t.v1z = 0.1234567890
    t.v2x = 0.1234567890
    t.v2y = 0.1234567890
    t.v2z = 0.1234567890
    t.v3x = 0.1234567890
    t.v3y = 0.1234567890
    t.v3z = 0.1234567890
    t.v4x = 0.1234567890
    t.v4y = 0.1234567890
    t.v4z = 0.1234567890
    t.v5x = 0.1234567890
    t.v5y = 0.1234567890
    t.v5z = 0.1234567890
    t.v6x = 0.1234567890
    t.v6y = 0.1234567890
    t.v6z = 0.1234567890
    t.v7x = 0.1234567890
    t.v7y = 0.1234567890
    t.v7z = 0.1234567890
    t.v8x = 0.1234567890
    t.v8y = 0.1234567890
    t.v8z = 0.1234567890
    t.grpx = 0.1234567890
    t.grpy = 0.1234567890
    t.grpz = 0.1234567890
    t.fullr = 1234567
    t.fullc = 1234567
    t.minr = 1234567
    t.maxr = 1234567
    t.minc = 1234567
    t.maxc = 1234567
    t.ie0 = 0.1234567890
    t.ier = 0.1234567890
    t.iec = 0.1234567890
    t.ierr = 0.1234567890
    t.ierc = 0.1234567890
    t.iecc = 0.1234567890
    t.ia0 = 0.1234567890
    t.iar = 0.1234567890
    t.iac = 0.1234567890
    t.iarr = 0.1234567890
    t.iarc = 0.1234567890
    t.iacc = 0.1234567890
    t.spx = 0.1234567890
    t.svx = 0.1234567890
    t.sax = 0.1234567890
    t.spy = 0.1234567890
    t.svy = 0.1234567890
    t.say = 0.1234567890
    t.spz = 0.1234567890
    t.svz = 0.1234567890
    t.saz = 0.1234567890
    fh = six.BytesIO()
    t.write_to_file(fh)
    # This can vary depending on roundoff, so don't compare.
    #assert fh.getvalue() == b'Blah'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreRSMIDA()
    t2.read_from_file(fh2)
    print(t2)
    assert t2.iid == 'abc'
    assert t2.edition == 'abc'
    assert t2.isid == 'abc'
    assert t2.sid == 'abc'
    assert t2.stid == 'abc'
    assert t2.year == 2017
    assert t2.month==12
    assert t2.day == 1
    assert t2.hour == 10
    assert t2.minute == 59
    assert t2.second == 12.5
    assert t2.grndd == 'G'
    assert t2.xuor == 1234.567890
    assert t2.yuor == 1234.567890
    assert t2.zuor == 1234.567890
    assert t2.xuxr == 0.1234567890
    assert t2.xuyr == 0.1234567890
    assert t2.xuzr == 0.1234567890
    assert t2.yuxr == 0.1234567890
    assert t2.yuyr == 0.1234567890
    assert t2.yuzr == 0.1234567890
    assert t2.zuxr == 0.1234567890
    assert t2.zuyr == 0.1234567890
    assert t2.zuzr == 0.1234567890
    assert t2.v1x == 0.1234567890
    assert t2.v1y == 0.1234567890
    assert t2.v1z == 0.1234567890
    assert t2.v2x == 0.1234567890
    assert t2.v2y == 0.1234567890
    assert t2.v2z == 0.1234567890
    assert t2.v3x == 0.1234567890
    assert t2.v3y == 0.1234567890
    assert t2.v3z == 0.1234567890
    assert t2.v4x == 0.1234567890
    assert t2.v4y == 0.1234567890
    assert t2.v4z == 0.1234567890
    assert t2.v5x == 0.1234567890
    assert t2.v5y == 0.1234567890
    assert t2.v5z == 0.1234567890
    assert t2.v6x == 0.1234567890
    assert t2.v6y == 0.1234567890
    assert t2.v6z == 0.1234567890
    assert t2.v7x == 0.1234567890
    assert t2.v7y == 0.1234567890
    assert t2.v7z == 0.1234567890
    assert t2.v8x == 0.1234567890
    assert t2.v8y == 0.1234567890
    assert t2.v8z == 0.1234567890
    assert t2.grpx == 0.1234567890
    assert t2.grpy == 0.1234567890
    assert t2.grpz == 0.1234567890
    assert t2.fullr == 1234567
    assert t2.fullc == 1234567
    assert t2.minr == 1234567
    assert t2.maxr == 1234567
    assert t2.minc == 1234567
    assert t2.maxc == 1234567
    assert t2.ie0 == 0.1234567890
    assert t2.ier == 0.1234567890
    assert t2.iec == 0.1234567890
    assert t2.ierr == 0.1234567890
    assert t2.ierc == 0.1234567890
    assert t2.iecc == 0.1234567890
    assert t2.ia0 == 0.1234567890
    assert t2.iar == 0.1234567890
    assert t2.iac == 0.1234567890
    assert t2.iarr == 0.1234567890
    assert t2.iarc == 0.1234567890
    assert t2.iacc == 0.1234567890
    assert t2.spx == 0.1234567890
    assert t2.svx == 0.1234567890
    assert t2.sax == 0.1234567890
    assert t2.spy == 0.1234567890
    assert t2.svy == 0.1234567890
    assert t2.say == 0.1234567890
    assert t2.spz == 0.1234567890
    assert t2.svz == 0.1234567890
    assert t2.saz == 0.1234567890

