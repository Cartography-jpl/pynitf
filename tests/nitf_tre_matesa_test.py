from pynitf.nitf_tre import *
from pynitf.nitf_tre_matesa import *
from pynitf_test_support import *
import io

def test_tre_matesa_basic():

    t = TreMATESA()

    t.cur_source = "Some file"
    t.cur_mate_type = "Some type"
    t.cur_file_id_len = 8
    t.cur_file_id = "abcdefgh"

    # Set some values
    t.num_groups = 2

    t.relationship[0] = "R1"
    t.num_mates[0] = 1
    t.source[0, 0] = "S1"
    t.mate_type[0, 0] = "T1"
    t.mate_id[0, 0] = b"I1"

    t.relationship[1] = "R1"
    t.num_mates[1] = 2
    t.source[1, 0] = "S1"
    t.mate_type[1, 0] = "T1"
    t.mate_id[1, 0] = b"I1"
    t.source[1, 1] = "S2"
    t.mate_type[1, 1] = "T2"

    t.mate_id[1, 1] = b"I23"

    fh = io.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'MATESA00323Some file                                 Some type       0008abcdefgh0002R1                      0001S1                                        T1              0002I1R1                      0002S1                                        T1              0002I1S2                                        T2              0003I23'
    fh2 = io.BytesIO(fh.getvalue())
    t2 = TreMATESA()
    t2.read_from_file(fh2)

    assert t2.cur_source == "Some file"
    assert t2.cur_mate_type == "Some type"
    assert t2.cur_file_id_len == 8
    assert t2.cur_file_id == "abcdefgh"

    assert t2.num_groups == 2

    assert t2.relationship[0] == "R1"
    assert t2.num_mates[0] == 1
    assert t2.source[0, 0] == "S1"
    assert t2.mate_type[0, 0] == "T1"
    assert t2.mate_id[0, 0] == "I1"

    assert t2.relationship[1] == "R1"
    assert t2.num_mates[1] == 2
    assert t2.source[1, 0] == "S1"
    assert t2.mate_type[1, 0] == "T1"
    assert t2.mate_id[1, 0] == "I1"
    assert t2.source[1, 1] == "S2"
    assert t2.mate_type[1, 1] == "T2"
    assert t2.mate_id[1, 1] == "I23"

    print (t2.summary())
