from pynitf.nitf_tre import *
from pynitf.nitf_tre_rsmpca import *
from pynitf_test_support import *
import io, six

def test_tre_rsmpca():
    t = TreRSMPCA()
    t.rsn = 1
    t.csn = 1
    t.rnrmo = 2881.0
    fh = six.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreRSMPCA()
    t2.read_from_file(fh2)
    print(t2)

    assert t.iid is None
    assert t2.iid is None
    assert t.rsn == 1
    assert t2.rsn == 1
    assert t.csn == 1
    assert t2.csn == 1
    assert t.rfep is None
    assert t2.rfep is None
    assert t.cfep is None
    assert t2.cfep is None
    assert t.rnrmo == 2881.0
    assert t2.rnrmo == 2881.0
