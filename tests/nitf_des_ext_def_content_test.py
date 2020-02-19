from pynitf.nitf_des_ext_def_content import *
from pynitf.nitf_file import *
from pynitf_test_support import *
import io, os

def test_basic():
    d = DesEXT_DEF_CONTENT()
    print (d.summary())

def test_file(isolated_dir):
    f = NitfFile()
    d = DesEXT_DEF_CONTENT(data_size=10)
    d.user_subheader.content_description = b"hi there"
    f.des_segment.append(NitfDesSegment(d))
    f.write("des_test.ntf")
    f2 = NitfFile("des_test.ntf")
    assert f2.des_segment[0].des.user_subheader.content_description == b"hi there"
    assert f2.des_segment[0].des.user_subheader.content_length == b"10"
    assert f2.des_segment[0].des.data_size == 10
    

def test_content_header():
    h = DesEXT_DEF_CONTENT.uh_class()
    h.content_type = b"ct"
    h.content_length = b"10"
    h.content_description = b"blah blah"
    h.content_disposition = b"caw caw"
    h.canonical_id = b"cid"
    h.des_id1 = b'foo'
    h.des_id2 = b'this is a foo'
    if(False):
        print(h.bytes())
    assert h.bytes() == b'Content-Type: ct\r\nContent-Use: \r\nContent-Length: 10\r\nContent-Description: blah blah\r\nContent-Disposition: caw caw\r\nCanonical-ID: cid\r\nDES-ID1: foo\r\nDES-ID2: this is a foo\r\n'
    h2 = DesEXT_DEF_CONTENT.uh_class()
    h2.content_headers = h.bytes()
    h2.parse()
    assert h2.content_type == b"ct"
    assert h2.content_length == b"10"
    assert h2.content_description == b"blah blah"
    assert h2.content_disposition == b"caw caw"
    assert h2.canonical_id == b"cid"
    assert h2.des_id1 == b'foo'
    assert h2.des_id2 == b'this is a foo'

@require_h5py    
def test_h5py_file(isolated_dir):
    h = h5py.File("test.h5", "w")
    g = h.create_group("TestGroup")
    g.create_dataset("test_data", data=b"hi there",
                     dtype=h5py.special_dtype(vlen=bytes))
    h.close()
    f = NitfFile()
    d = DesEXT_h5(file="test.h5")
    d.user_subheader.content_description = b"hi there"
    f.des_segment.append(NitfDesSegment(d))
    f.write("des_test.ntf")
    f2 = NitfFile("des_test.ntf")
    assert f2.des_segment[0].des.user_subheader.content_description == b"hi there"
    assert f2.des_segment[0].des.user_subheader.content_length == str(os.path.getsize("test.h5")).encode("utf-8")
    assert f2.des_segment[0].des.data_size == os.path.getsize("test.h5")
    print(f2.des_segment[0].des)
    assert isinstance(f2.des_segment[0].des, DesEXT_h5)
    print(f2.des_segment[0].des)
    assert f2.des_segment[0].des.h5py_fh["TestGroup/test_data"][()] == b'hi there'
    
    
    
