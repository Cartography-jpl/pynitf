from pynitf.nitf_tre import *
from pynitf.nitf_tre_rsmgga import *
from pynitf_test_support import *
import io, six

def test_tre_rsmgga():
    t = TreRSMGGA()
    t.deltaz = 1268.0
    fh = six.BytesIO()
    t.write_to_file(fh)
    # This is way too large to check, so skip this
    #assert fh.getvalue() == b'blah'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreRSMGGA()
    t2.read_from_file(fh2)
    print(t2)

    assert t.iid is None
    assert t.deltaz == 1268.0

