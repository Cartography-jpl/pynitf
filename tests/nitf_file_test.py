from pynitf.nitf_file import *
from pynitf.nitf_tre_csde import *
from pynitf.nitf_tre_csepha import *
from pynitf.nitf_tre_csexrb import *
from pynitf.nitf_tre_piae import *
from pynitf.nitf_tre_rpc import *
from pynitf.nitf_tre_geosde import *
from pynitf.nitf_des_csatta import *
from pynitf.nitf_des_cssfab import *
from pynitf.nitf_image import *
from pynitf.nitf_tre import *
from pynitf_test_support import *
import pynitf.nitf_field
import pynitf.nitf_des
import subprocess
import os
import json
import six
import numpy as np
import filecmp

# Turn on debug messages
#pynitf.nitf_field.DEBUG = True
#pynitf.nitf_des.DEBUG = True

# Do these in a few places, so collect in one spot.
def create_image_seg(f, security = None):
    img = NitfImageWriteNumpy(9, 10, np.uint8)
    if(security):
        img.security = security
    for i in range(9):
        for j in range(10):
            img[0, i,j] = i * 10 + j
    f.image_segment.append(NitfImageSegment(img))

def create_tre(f):
    t = TreUSE00A()
    t.angle_to_north = 270
    t.mean_gsd = 105.2
    t.dynamic_range = 2047
    t.obl_ang = 34.12
    t.roll_ang = -21.15
    t.n_ref = 0
    t.rev_num = 3317
    t.n_seg = 1
    t.max_lp_seg = 6287
    t.sun_el = 68.5
    t.sun_az = 131.3
    f.tre_list.append(t)

def create_tre2(f):
    t = TreUSE00A()
    t.angle_to_north = 290
    t.mean_gsd = 105.2
    t.dynamic_range = 2047
    t.obl_ang = 34.12
    t.roll_ang = -21.15
    t.n_ref = 0
    t.rev_num = 3317
    t.n_seg = 1
    t.max_lp_seg = 6287
    t.sun_el = 68.5
    t.sun_az = 131.3
    f.tre_list.append(t)
    
def check_tre(t):    
    assert t.tre_tag == "USE00A"
    assert t.angle_to_north == 270
    assert_almost_equal(t.mean_gsd, 105.2)
    assert t.dynamic_range == 2047
    assert_almost_equal(t.obl_ang, 34.12)
    assert_almost_equal(t.roll_ang, -21.15)
    assert t.n_ref == 0
    assert t.rev_num == 3317
    assert t.n_seg == 1
    assert t.max_lp_seg == 6287
    assert_almost_equal(t.sun_el, 68.5)
    assert_almost_equal(t.sun_az, 131.3)

def check_tre2(t):    
    assert t.tre_tag == "USE00A"
    assert t.angle_to_north == 290
    assert_almost_equal(t.mean_gsd, 105.2)
    assert t.dynamic_range == 2047
    assert_almost_equal(t.obl_ang, 34.12)
    assert_almost_equal(t.roll_ang, -21.15)
    assert t.n_ref == 0
    assert t.rev_num == 3317
    assert t.n_seg == 1
    assert t.max_lp_seg == 6287
    assert_almost_equal(t.sun_el, 68.5)
    assert_almost_equal(t.sun_az, 131.3)

def create_text_segment(f, security = None):
    d = {
        'first_name': 'Guido',
        'second_name': 'Rossum',
        'titles': ['BDFL', 'Developer'],
    }
    ts = NitfTextSegment(txt = json.dumps(d))
    ts.subheader.textid = 'ID12345'
    ts.subheader.txtalvl = 0
    ts.subheader.txtitl = 'sample title'
    if(security):
        ts.security = security
    f.text_segment.append(ts)

def create_des(f, security = None):
    des = DesCSATTA()
    if(security):
        des.security = security
    des.att_type = 'ORIGINAL'
    des.dt_att = '900.5000000000'
    des.date_att = 20170501
    des.t0_att = '235959.100001'
    des.num_att = 5
    for n in range(des.num_att):
        des.att_q1[n] = 10.1
        des.att_q2[n] = 10.1
        des.att_q3[n] = 10.1
        des.att_q4[n] = 10.1

    de = NitfDesSegment(des=des)
    f.des_segment.append(de)
    
def print_diag(f):
    '''Print out diagnostic information, useful to make sure the file
    we generate is valid.'''
    if(True):
        print(f)
        # Don't fail if the command does exist, but if we have it run
        # gdalinfo and show_nitf++ on the file
        #
        # gdalinfo is part of GDAL, show_nitf++ is part of Nitro
        if(cmd_exists("gdalinfo")):
            if sys.version_info > (3,):
                subprocess.run(["gdalinfo", "-mdd", "xml:TRE", "z.ntf"])
            else:
                subprocess.call(["gdalinfo", "-mdd", "xml:TRE", "z.ntf"])
        if(cmd_exists("show_nitf++")):
            if sys.version_info > (3,):
                subprocess.run(["show_nitf++", "z.ntf"])
            else:
                subprocess.call(["show_nitf++", "z.ntf"])

def create_sample():
#def test_create_sample():
    '''Create sample.ntf file we can then use for testing'''
    subprocess.run(["vicarb", "gen", "x"])
    subprocess.run(["gdal_to_nitf", "x", unit_test_data + "sample.ntf"])
    
def test_basic_read():
    f = NitfFile(unit_test_data + "sample.ntf")
    assert len(f.image_segment) == 1
    img = f.image_segment[0].data
    assert img.shape == (1, 10, 10)
    for i in range(10):
        for j in range(10):
            assert img[0, i,j] == i + j
    if(False):
        print(f)

def test_read_tre():
    f = NitfFile(unit_test_data + "test_use00a.ntf")
    assert len(f.image_segment) == 1
    assert len(f.image_segment[0].tre_list) == 1
    check_tre(f.image_segment[0].tre_list[0])
    if(False):
        print(f)
        
def test_basic_write(isolated_dir):
    f = NitfFile()
    create_image_seg(f)
    create_tre(f)
    create_tre2(f.image_segment[0])
    f.write("z.ntf")
    f2 = NitfFile("z.ntf")
    assert len(f2.image_segment) == 1
    img = f2.image_segment[0].data
    assert img.shape == (1, 9, 10)
    for i in range(9):
        for j in range(10):
            assert img[0, i,j] == i * 10 + j
    assert len(f2.tre_list) == 1
    assert len(f2.image_segment[0].tre_list) == 1
    check_tre(f2.tre_list[0])
    check_tre2(f2.image_segment[0].tre_list[0])
    print_diag(f2)

def test_large_tre_write(isolated_dir):
    '''Repeat of test_basic_write, but also include a really big TRE that
    forces the use of the second place in the header for TREs'''
    desc = ["BIGTRE",
            ["big_field", "", 99999-20, str]
            ]
    TreBig = create_nitf_tre_structure("TreBig", desc)
    f = NitfFile()
    create_image_seg(f)
    f.tre_list.append(TreBig())
    f.image_segment[0].tre_list.append(TreBig())
    create_tre(f)
    create_tre2(f.image_segment[0])
    f.write("z.ntf")
    # Write a second time. We had a bug where the tre would appear twice,
    # once when we write the tre_list and once when the old tre overflow des
    # get copied. Test to make sure that writing twice still returns the
    # same lists of TREs
    f.write("z2.ntf")
    f2 = NitfFile("z.ntf")
    f3 = NitfFile("z2.ntf")
    assert len(f2.image_segment) == 1
    assert len(f3.image_segment) == 1
    img = f2.image_segment[0].data
    img2 = f3.image_segment[0].data
    assert img.shape == (1, 9, 10)
    assert img2.shape == (1, 9, 10)
    for i in range(9):
        for j in range(10):
            assert img[0, i,j] == i * 10 + j
            assert img2[0, i,j] == i * 10 + j
    assert len(f2.tre_list) == 2
    assert len(f3.tre_list) == 2
    assert len(f2.image_segment[0].tre_list) == 2
    assert len(f3.image_segment[0].tre_list) == 2
    check_tre([tre for tre in f2.tre_list if tre.tre_tag == "USE00A"][0])
    check_tre([tre for tre in f3.tre_list if tre.tre_tag == "USE00A"][0])
    check_tre2([tre for tre in f2.image_segment[0].tre_list if tre.tre_tag == "USE00A"][0])
    check_tre2([tre for tre in f3.image_segment[0].tre_list if tre.tre_tag == "USE00A"][0])
    print_diag(f2)
    print_diag(f3)
    assert filecmp.cmp("z.ntf", "z2.ntf", shallow=False)
    
def test_tre_overflow_write(isolated_dir):
    '''Repeat of test_basic_write, but also include two really big TREs that
    forces the use of the DES TRE overflow for TREs'''
    desc = ["BIGTRE",
            ["big_field", "", 99999-20, str]
            ]
    TreBig = create_nitf_tre_structure("TreBig", desc)
    f = NitfFile()
    create_image_seg(f)
    f.tre_list.append(TreBig())
    f.tre_list.append(TreBig())
    f.image_segment[0].tre_list.append(TreBig())
    f.image_segment[0].tre_list.append(TreBig())
    create_tre(f)
    create_tre2(f.image_segment[0])
    f.write("z.ntf")
    # Write a second time. We had a bug where the tre would appear twice,
    # once when we write the tre_list and once when the old tre overflow des
    # get copied. Test to make sure that writing twice still returns the
    # same lists of TREs
    f.write("z2.ntf")
    f2 = NitfFile("z.ntf")
    f3 = NitfFile("z2.ntf")
    assert len(f2.image_segment) == 1
    assert len(f3.image_segment) == 1
    img = f2.image_segment[0].data
    img2 = f3.image_segment[0].data
    assert img.shape == (1, 9, 10)
    assert img2.shape == (1, 9, 10)
    for i in range(9):
        for j in range(10):
            assert img[0, i,j] == i * 10 + j
            assert img2[0, i,j] == i * 10 + j
    assert len(f2.tre_list) == 3
    assert len(f3.tre_list) == 3
    assert len(f2.image_segment[0].tre_list) == 3
    assert len(f3.image_segment[0].tre_list) == 3
    check_tre([tre for tre in f2.tre_list if tre.tre_tag == "USE00A"][0])
    check_tre([tre for tre in f3.tre_list if tre.tre_tag == "USE00A"][0])
    check_tre2([tre for tre in f2.image_segment[0].tre_list if tre.tre_tag == "USE00A"][0])
    check_tre2([tre for tre in f3.image_segment[0].tre_list if tre.tre_tag == "USE00A"][0])
    with open("f.txt", "w") as fh:
        print(str(f), file=fh)
    with open("f2.txt", "w") as fh:
        print(str(f2), file=fh)
    with open("f3.txt", "w") as fh:
        print(str(f3), file=fh)
    # Actually this is ok, just stuff is in a different order. No easy way
    # to check, so we just skip this.
    assert str(f2) == str(f3)
    print_diag(f2)
    print_diag(f3)
    assert filecmp.cmp("z.ntf", "z2.ntf", shallow=False)
    
def test_read_quickbird(nitf_sample_quickbird):
    f = NitfFile(nitf_sample_quickbird)
    print(f.summary())
    print(f)

def test_read_worldview(nitf_sample_wv2):
    f = NitfFile(nitf_sample_wv2)
    print(f.summary())
    print(f)

def test_read_ikonos(nitf_sample_ikonos):
    f = NitfFile(nitf_sample_ikonos)
    print(f.summary())
    print(f)

def test_read_rip(nitf_sample_rip):
    '''Test reading the reference SNIP sample file'''
    f = NitfFile(nitf_sample_rip)
    print(f.summary())
    print(f)
    
def test_copy_quickbird(nitf_sample_quickbird):
    '''Test copying a quickbird NITF file. It creates a copy of the file
    and then reads it back and compares the str() result to that of
    the original file
    '''
    f = NitfFile(nitf_sample_quickbird)
    original_output = str(f)
    fname_copy = "quickbird_copy.ntf"
    f.write(fname_copy)
    copy_output = str(NitfFile(fname_copy))
    assert original_output == copy_output

def test_copy_worldview(nitf_sample_wv2):
    '''Test copying a worldview NITF file. It creates a copy of the file
    and then reads it back and compares the str() result to that of
    the original file
    '''
    # Some of the DESs aren't implemented yet. Just copy these over for
    # now, so we can test everything we do have.
    try:
        pynitf.register_des_class(pynitf.NitfDesCopy, priority_order=999)
        f = NitfFile(nitf_sample_wv2)
        original_output = str(f)
        fname_copy = "worldview_copy.ntf"
        f.write(fname_copy)
        copy_output = str(NitfFile(fname_copy))
        with open("f1.txt", "w") as fh:
            print(original_output, file=fh)
        with open("f2.txt", "w") as fh:
            print(copy_output, file=fh)
        # This is different, but just because the original worldview file put
        # some of the TREs in the TRE_OVERFLOW DES, when they actually fit
        # in the normal TRE header. So we have the same content, just a
        # different arrangement. Don't have a easy way to test this, so we
        # just skip the actual check. Can compare f1.txt and f2.txt manually
        # if you want to verify the content.
        #assert original_output == copy_output
    finally:
        # Remove, so this doesn't affect other tests
        pynitf.unregister_des_class(pynitf.NitfDesCopy)

def test_copy_ikonos(nitf_sample_ikonos):
    '''Test copying a ikonos NITF file. It creates a copy of the file and
    then reads it back and compares the str() result to that of the
    original file
    '''
    f = NitfFile(nitf_sample_ikonos)
    original_output = str(f)
    fname_copy = "ikonos_copy.ntf"
    f.write(fname_copy)
    copy_output = str(NitfFile(fname_copy))
    assert original_output == copy_output

def test_copy_rip(nitf_sample_rip):
    '''Test copying a ikonos NITF file. It creates a copy of the file and
    then reads it back and compares the str() result to that of the
    original file
    '''
    f = NitfFile(nitf_sample_rip)
    original_output = str(f)
    fname_copy = "rip_copy.ntf"
    f.write(fname_copy)
    copy_output = str(NitfFile(fname_copy))
    assert original_output == copy_output
    
def test_full_file(isolated_dir):
    '''This create an end to end NITF file, this was at least initially the
    same as basic_nitf_example.py but as a unit test.'''

    # Create the file. We don't supply a name yet, that comes when we actually
    # write
    
    f = NitfFile()
    create_image_seg(f)
    create_tre(f)
    create_tre2(f)
    create_text_segment(f)
    create_des(f)
    print(f)
    f.write("basic_nitf.ntf")
    f2 = NitfFile("basic_nitf.ntf")
    print(f2)
    print("Image Data:")
    print(f2.image_segment[0].data.data)

    print("Text Data:")
    print(f2.text_segment[0].data)        

def test_full_file_security(isolated_dir):
    '''This create an end to end NITF file, this was at least initially the
    same as basic_nitf_example.py but as a unit test.

    This variation sets the NitfSecurity to a fake security, so we can test
    reading and writing this.'''

    # Create the file. We don't supply a name yet, that comes when we actually
    # write
    
    f = NitfFile(security=security_fake)
    create_image_seg(f, security=security_fake)
    create_tre(f)
    create_tre2(f)
    create_text_segment(f, security=security_fake)
    create_des(f, security=security_fake)
    print(f)
    f.write("basic_nitf.ntf")
    f2 = NitfFile("basic_nitf.ntf")
    print(f2)
    print("Image Data:")
    print(f2.image_segment[0].data.data)

    print("Text Data:")
    print(f2.text_segment[0].data)        
    
