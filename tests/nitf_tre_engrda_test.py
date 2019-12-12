from pynitf.nitf_tre import *
from pynitf.nitf_tre_engrda import *
from pynitf.nitf_file import *
from pynitf_test_support import *
import io, six

def test_tre_engrda():
    '''Basic test of engrda. This comes from N.6 of the documentation, 
    which gives several examples. Note that this uses the low level 
    interface, see create_engrda below for a nicer higher level interface'''
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
    assert t.engdatc[0] == t.engmtxc[0]*t.engmtxr[0]
    t.engdata[0]= b'\x01\x25'

    t.englbl[1] = b"TEMP2"
    t.engmtxc[1]=1
    t.engmtxr[1]=1
    t.engtyp[1]="R"
    t.engdts[1]=4
    t.engdatu[1]="tK"
    # Should have this automatically calculated
    assert t.engdatc[1] == t.engmtxc[1]*t.engmtxr[1]
    t.engdata[1]= b'\x03\x27\x12\x76'
    t.englbl[2] = b"TEMP3 Wall"
    t.engmtxc[2]=10
    t.engmtxr[2]=1
    t.engtyp[2]="A"
    t.engdts[2]=1
    t.engdatu[2]="NA"
    # Should have this automatically calculated
    assert t.engdatc[2] == t.engmtxc[2]*t.engmtxr[2]
    t.engdata[2]= b"10.7 DEG C"
    
    fh = six.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b"ENGRDA00125My_sensor           00305TEMP100010001I2tC00000001\x01%05TEMP200010001R4tK00000001\x03'\x12v10TEMP3 Wall00100001A1NA0000001010.7 DEG C"
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
    assert t.engdata[0] == b'\x01\x25'
    assert t.engdata[1] == b'\x03\x27\x12\x76'
    assert t.engdata[2] == b"10.7 DEG C"

    print ("\n" + t.summary())

    # We want to give a simpler interface, where we can read and write
    # numpy arrays


def create_engrda(resrc = "My_sensor"):
    t = TreENGRDA()
    t.resrc = resrc
    t["TEMP1"] = (np.array([277], dtype = np.uint16), "tC")
    t["TEMP2"] = (np.array([277.45], dtype = np.float32), "tK")
    t["TEMP3 Wall"] = ("10.7 DEG C", "NA")
    return t

def test_file_engrda(isolated_dir):
    '''Test have ENGRDA as part of a file, including accessing as a hash.'''
    f = NitfFile()
    f.tre_list.append(create_engrda(resrc = "My_sensor 1"))
    f.tre_list.append(create_engrda(resrc = "My_sensor 2"))
    f.tre_list.append(create_engrda(resrc = "My_sensor 3"))
    f.write("z.ntf")
    f2 = NitfFile("z.ntf")
    assert len(f2.engrda.keys()) == 3
    assert all(t in f2.engrda.keys() for t in ["My_sensor 1", "My_sensor 2",
                                               "My_sensor 3"])
    print(f2)
    f3 = NitfFile()
    f3.tre_list.append(f2.engrda["My_sensor 1"])
    f3.tre_list.append(f2.engrda["My_sensor 3"])
    f3.write("z.ntf")
    f4 = NitfFile("z.ntf")
    assert len(f4.engrda.keys()) == 2
    assert all(t in f4.engrda.keys() for t in ["My_sensor 1", "My_sensor 3"])
    assert f4.engrda["My_sensor 1"]["TEMP3 Wall"] == ("10.7 DEG C", "NA")
    assert f4.engrda["My_sensor 1"]["TEMP1"] == (np.array([[277,]], dtype = np.dtype(">u2")), "tC")
    assert f4.engrda["My_sensor 1"]["TEMP2"] == (np.array([[277.45,]], dtype = np.dtype(">f4")), "tK")
    
    
