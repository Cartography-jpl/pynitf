from pynitf.nitf_tre import *
from pynitf.nitf_tre_engrda import *
from test_support import *
import io, six

def test_tre_engrda():
    '''Basic test of engrda. This comes from N.6 of the documentation, 
    which gives several examples'''
    t = TreENGRDA()
    t.resrc = "My_sensor"
    t.recnt=3
    t.englbl[0] = b"TEMP1"
    t.engmtxc[0]=1
    t.engmtxr[0]=1
    t.engtyp[0]="I"
    t.engdts[0]=2
    t.engdatu[0]="tC"
    # Should have this automatically calculated
    t.engdatc[0]=t.engmtxc[0]*t.engmtxr[0]
    t.engdata[0]= b'00'

    t.englbl[1] = b"TEMP2"
    t.engmtxc[1]=1
    t.engmtxr[1]=1
    t.engtyp[1]="R"
    t.engdts[1]=4
    t.engdatu[1]="tK"
    # Should have this automatically calculated
    t.engdatc[1]=t.engmtxc[1]*t.engmtxr[1]
    t.engdata[1]= b'0000'
    t.englbl[2] = b"TEMP3 Wall"
    t.engmtxc[2]=10
    t.engmtxr[2]=1
    t.engtyp[2]="A"
    t.engdts[2]=1
    t.engdatu[2]="NA"
    # Should have this automatically calculated
    t.engdatc[2]=t.engmtxc[2]*t.engmtxr[2]
    t.engdata[2]= b"10.7 DEG C"
    
    fh = six.BytesIO()
    t.write_to_file(fh)
    #print(fh.getvalue())
    assert fh.getvalue() == b'ENGRDA00125My_sensor           00305TEMP100010001I2tC000000010005TEMP200010001R4tK00000001000010TEMP3 Wall00100001A1NA0000001010.7 DEG C'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreENGRDA()
    t2.read_from_file(fh2)
    assert t2.resrc == "My_sensor"
    assert t2.recnt == 3
    # These dynamically filled in
    assert list(t2.engln) == [5, 5, 10]
    assert list(t2.englbl) == [b"TEMP1", b"TEMP2", b"TEMP3 Wall"]
    assert list(t2.engmtxc) == [1,1,10]
    assert list(t2.engmtxr) == [1,1,1]
    assert list(t2.engtyp) == ["I", "R", "A"]
    assert t.engdata[0] == b'00'
    assert t.engdata[1] == b'0000'
    assert t.engdata[2] == b"10.7 DEG C"

    print ("\n" + t.summary())

    # We want to give a simpler interface, where we can read and write
    # numpy arrays

