from pynitf.nitf_tre import *
from pynitf.nitf_tre_matesa import *
from pynitf_test_support import *
import io, six

def test_tre_matesa_basic():

    t = TreMATESA()

    # Set some values
    t.num_groups = 2

    t.relationship[0] = "R1"
    t.num_mates[0] = 1
    t.source[0, 0] = "S1"
    t.id_type[0, 0] = "T1"
    t.mate_id[0, 0] = "I1"

    t.relationship[1] = "R1"
    t.num_mates[1] = 2
    t.source[1, 0] = "S1"
    t.id_type[1, 0] = "T1"
    t.mate_id[1, 0] = "I1"
    t.source[1, 1] = "S2"
    t.id_type[1, 1] = "T2"
    t.mate_id[1, 1] = "I2"

    fh = six.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'MATESA0102602R1                              001S1                                        T1                  I1                                                                                                                                                                                                                                                              R1                              002S1                                        T1                  I1                                                                                                                                                                                                                                                              S2                                        T2                  I2                                                                                                                                                                                                                                                              '

    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreMATESA()
    t2.read_from_file(fh2)
    assert t2.num_groups == 2

    assert t.relationship[0] == "R1"
    assert t.num_mates[0] == 1
    assert t.source[0, 0] == "S1"
    assert t.id_type[0, 0] == "T1"
    assert t.mate_id[0, 0] == "I1"

    assert t.relationship[1] == "R1"
    assert t.num_mates[1] == 2
    assert t.source[1, 0] == "S1"
    assert t.id_type[1, 0] == "T1"
    assert t.mate_id[1, 0] == "I1"
    assert t.source[1, 1] == "S2"
    assert t.id_type[1, 1] == "T2"
    assert t.mate_id[1, 1] == "I2"

    print (t2.summary())
