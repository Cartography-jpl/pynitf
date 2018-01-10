from pynitf.nitf_tre import *
from pynitf.nitf_tre_pixqla import *
from test_support import *
import io, six

def test_tre_pixqla():
    '''Basic test pf pixqla'''
    t = TrePIXQLA()
    t.numais = 10
    for i in range(int(t.numais)):
        t.aisdlvl[i] = 5+i
    t.npixqual = 2
    t.pq_condition[0] = "Condition 1"
    t.pq_condition[1] = "Condition 2"
    fh = six.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'PIXQLA0011810 00500600700800901001101201301400021Condition 1                             Condition 2                             '
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TrePIXQLA()
    t2.read_from_file(fh2)
    assert t.numais == "10"
    assert list(t.aisdlvl) == [5,6,7,8,9,10,11,12,13,14]
    assert t.npixqual == 2
    assert t.pq_bit_value == "1"
    assert list(t.pq_condition) == ["Condition 1", "Condition 2"]

    print(t2.summary())

def test_tre_pixqla_with_all():
    '''Repeat basic test pf pixqla, but have numais set to 'ALL' and make sure
    we have proper handling'''
    t = TrePIXQLA()
    t.numais = "ALL"
    t.npixqual = 2
    t.pq_condition[0] = "Condition 1"
    t.pq_condition[1] = "Condition 2"
    fh = six.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'PIXQLA00088ALL00021Condition 1                             Condition 2                             '
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TrePIXQLA()
    t2.read_from_file(fh2)
    assert t.numais == "ALL"
    assert list(t.aisdlvl) == []
    assert t.npixqual == 2
    assert t.pq_bit_value == "1"
    assert list(t.pq_condition) == ["Condition 1", "Condition 2"]

    
    
    
