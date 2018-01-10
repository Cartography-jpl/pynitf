from pynitf.nitf_file_header import *
from pynitf.nitf_image_subheader import *
from pynitf.nitf_image import *
from test_support import *
import io,six

def test_basic_read():
    t = NitfFileHeader()
    t2 = NitfImageFromNumpy()
    with open(unit_test_data + "sample.ntf", 'rb') as fh:
        t.read_from_file(fh)
        t2.image_subheader.read_from_file(fh)
        t2.read_from_file(fh)
    assert t2.data.shape == (10, 10)
    for i in range(10):
        for j in range(10):
            assert t2.data[i,j] == i + j
    t2 = NitfImageFromNumpy(nrow=10, ncol=10)
    assert t2.data.shape == (10, 10)
    for i in range(10):
        for j in range(10):
            t2.data[i,j] = i + j
    fh = six.BytesIO()
    t2.write_to_file(fh)
    assert fh.getvalue() == b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12'

    
    
    
    

    
