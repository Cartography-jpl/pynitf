from pynitf.nitf_file import *
from pynitf.nitf_des_cscsdb import *
from pynitf_test_support import *
import pynitf.nitf_field

#pynitf.nitf_field.DEBUG = True
#pynitf.nitf_des.DEBUG = True

def test_read_rip(nitf_sample_rip):
    '''Test reading the reference SNIP sample file'''
    f = NitfFile(nitf_sample_rip)
    d = [d for d in f.des_segment if d.subheader.desid == "CSCSDB"][0]
    print(d)
    

