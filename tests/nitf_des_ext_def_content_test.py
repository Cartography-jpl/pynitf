from pynitf.nitf_des_ext_def_content import *
from pynitf_test_support import *
import io, six

def test_basic():

    d = DesEXT_DEF_CONTENT()
    print (d.summary())

def test_udsh():

    d = DesEXT_DEF_CONTENT_UH()

    d.content_headers_len = 4
    d.content_headers = b'\x03\x27\x12\x76'

    fh = six.BytesIO()
    d.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'0004\x03\'\x12v'
    fh2 = six.BytesIO(fh.getvalue())
    d2 = DesEXT_DEF_CONTENT_UH()
    d2.read_from_file(fh2)

    assert d2.content_headers_len == 4
    assert d2.content_headers == b'\x03\x27\x12\x76'

    print (d2)