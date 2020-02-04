from pynitf.nitf_tre import *
from pynitf.nitf_tre_rsmpia import *
from pynitf_test_support import *
import io

def test_tre_rsmpia():
    t = TreRSMPIA()
    t.rnis = 3
    t.cnis = 2
    t.cssiz = 13763.0
    fh = io.BytesIO()
    t.write_to_file(fh)
    # This can vary depending on roundoff, so don't compare.
    #assert fh.getvalue() == b'Blah'
    fh2 = io.BytesIO(fh.getvalue())
    t2 = TreRSMPIA()
    t2.read_from_file(fh2)
    print(t2)
    assert t2.cssiz == 13763.0


