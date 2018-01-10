from pynitf.nitf_tre import *
from pynitf.nitf_tre_rsmgia import *
from pynitf_test_support import *
import io, six

def test_tre_rsmpia():
    t = TreRSMGIA()
    t.grnis = 3
    t.gcnis = 2
    t.gcssiz = 13763.0
    fh = six.BytesIO()
    t.write_to_file(fh)
    # This can vary depending on roundoff, so don't compare.
    #assert fh.getvalue() == b'Blah'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreRSMGIA()
    t2.read_from_file(fh2)
    print(t2)
    assert t2.gcssiz == 13763.0
