from pynitf.nitf_tre import *
from pynitf.nitf_tre_histoa import *
from pynitf_test_support import *
import io
    
def test_basic():

    numEvents = 2

    t = TreHISTOA()

    #Set some values
    t.systype = "SYSTEM_TYPE"
    t.pc = "NO_COMPRESSI"
    t.pe = "NONE"
    t.remap_flag = "0"
    t.lutid = 0
    t.nevents = numEvents

    for i in range(numEvents):
        t.pdate[i] = "20170615121212"
        t.psite[i] = "ABCDEFGHIJ"
        t.pas[i] = "AAAAAAAAAA"
        t.nipcom[i] = 2
        t.ipcom[i, 0] = "HELLO1"
        t.ipcom[i, 1] = "HELLO2"

    fh = io.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'HISTOA00509SYSTEM_TYPE         NO_COMPRESSINONE0000220170615121212ABCDEFGHIJAAAAAAAAAA2HELLO1                                                                          HELLO2                                                                          00              0 00000000             20170615121212ABCDEFGHIJAAAAAAAAAA2HELLO1                                                                          HELLO2                                                                          00              0 00000000             '
    fh2 = io.BytesIO(fh.getvalue())
    t2 = TreHISTOA()
    t2.read_from_file(fh2)
    assert t2.systype == "SYSTEM_TYPE"
    assert t2.pc == "NO_COMPRESSI"
    assert t2.pe == "NONE"
    assert t2.remap_flag == "0"
    assert t2.lutid == 0
    assert t2.nevents == numEvents

    for i in range(numEvents):
        assert t2.pdate[i] == "20170615121212"
        assert t2.psite[i] == "ABCDEFGHIJ"
        assert t2.pas[i] == "AAAAAAAAAA"
        assert t2.nipcom[i] == 2
        assert t2.ipcom[i, 0] == "HELLO1"
        assert t2.ipcom[i, 1] == "HELLO2"

    print (t2.summary())
