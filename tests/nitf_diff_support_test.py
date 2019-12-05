import subprocess
import os
import json
import six
import numpy as np
import logging
import h5py
from pynitf.nitf_file import *
from pynitf.nitf_tre_csde import *
from pynitf.nitf_tre_csepha import *
from pynitf.nitf_tre_piae import *
from pynitf.nitf_tre_rpc import *
from pynitf.nitf_tre_geosde import *
from pynitf.nitf_des_csattb import *
from pynitf.nitf_image import *
from pynitf.nitf_image_subheader import *
from pynitf.nitf_des_ext_def_content import *
from pynitf.nitf_tre import *
from pynitf_test_support import *
from pynitf.nitf_diff_support import *

# Do these in a few places, so collect in one spot.
def create_image_seg(f, iid1 = '', num = 10, bias = 0, adjust = None):
    img = NitfImageWriteNumpy(9, 10, np.uint8)
    for i in range(9):
        for j in range(10):
            img[0, i, j] = (i * num + j) + bias

    if adjust is not None:
        for adjustment in adjust:
            img[0, adjustment[0], adjustment[1]] = adjustment[2]

    image_seg = NitfImageSegment(img)
    subheader = image_seg.subheader
    subheader.iid1 = iid1
    f.image_segment.append(image_seg)
    return image_seg

def create_tre(f, atn = 270):
    t = TreUSE00A()
    t.angle_to_north = atn
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
    
def create_text_segment(f, first_name = 'Guido', textid = 'ID12345'):
    d = {
        'first_name': first_name,
        'second_name': 'Rossum',
        'titles': ['BDFL', 'Developer'],
    }
    ts = NitfTextSegment(txt = json.dumps(d))
    ts.subheader.textid = textid
    ts.subheader.txtalvl = 0
    ts.subheader.txtitl = 'sample title'
    f.text_segment.append(ts)

def create_des(f, date_att = 20170501, q = 0.1):

    ds = DesCSATTB_UH()
    ds.id = '4385ab47-f3ba-40b7-9520-13d6b7a7f311'
    ds.numais = '010'
    for i in range(int(ds.numais)):
        ds.aisdlvl[i] = 5 + i
    ds.reservedsubh_len = 0

    des = DesCSATTB(user_subheader=ds)
    des.qual_flag_att = 1
    des.interp_type_att = 1
    des.att_type = 1
    des.eci_ecf_att = 0
    des.dt_att = 900.5
    des.date_att = 20170501
    des.t0_att = 235959.100001000
    des.num_att = 5
    for n in range(des.num_att):
        des.q1[n] = q
        des.q2[n] = q
        des.q3[n] = q
        des.q4[n] = q
    des.reserved_len = 0

    de = NitfDesSegment(des=des)
    f.des_segment.append(de)

def create_basic_nitf():
    f = NitfFile()
    create_tre(f)
    create_tre2(f)
    create_text_segment(f)

    return f

def test_nitf_diff_neq_one_val(isolated_dir):
    f = NitfFile()
    create_tre(f)
    f.write("basic_nitf.ntf")

    f = NitfFile()
    create_tre2(f)
    f.write("basic2_nitf.ntf")

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf") == False

def test_nitf_diff_eq(isolated_dir):
    '''This create an end to end NITF file, this was at least initially the
    same as basic_nitf_example.py but as a unit test.'''

    # Create the file. We don't supply a name yet, that comes when we actually
    # write
    
    f = create_basic_nitf()

    iseg = create_image_seg(f, iid1 = 'An IID1')
    #create_tre(iseg, atn = 43)
    create_tre(iseg)

    # Using the alternate desid of to break the diff, as it should.
    create_des(f)
    #create_des(f)

    f2 = create_basic_nitf()
    # This exercises the nitf_image_subheader eq_string_ignore_case function used by the iid1 field.
    iseg2 = create_image_seg(f2, 'an iid1')
    create_tre(iseg2)

    create_des(f2)

    f.write("basic_nitf.ntf")
    f2.write("basic2_nitf.ntf")

    logger=logging.getLogger("nitf_diff")
    # This doesn't seem to have the desired effect, so I created
    # pytest.ini to set the logging level - wlb
    logging.basicConfig(level=logging.DEBUG)

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf") == True

    # This excludes image header field iid1 from comparison
    #assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf", exclude=['image.iid1'])
    # This compares only image header field iid1
    #assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf", include=['image.iid1'])


def test_nitf_diff_neq_des(isolated_dir):
    '''This create an end to end NITF file, this was at least initially the
    same as basic_nitf_example.py but as a unit test.'''

    # Create the file. We don't supply a name yet, that comes when we actually
    # write

    f = NitfFile()

    # clevel default is 3, so this breaks the diff as it should.
    # f.file_header.clevel = 2

    # Using the alternate atn of 42 breaks the diff, as it should. It
    # complains that both angle_to_north and xhd differ, because the
    # tre is written as part of the xhd. Incidentally, USE00A is an
    # image TRE, but it works fine here for testing file TRE
    # differencing.
    # create_tre(f, atn = 42)
    create_tre(f)

    create_tre2(f)

    iseg = create_image_seg(f, iid1='An IID1')
    # create_tre(iseg, atn = 43)
    create_tre(iseg)

    create_text_segment(f)

    # Using the alternate desid of to break the diff, as it should.
    create_des(f)
    # create_des(f)

    f2 = NitfFile()
    create_tre(f2)
    create_tre2(f2)
    # This exercises the nitf_image_subheader eq_string_ignore_case function used by the iid1 field.
    iseg2 = create_image_seg(f2, 'an iid1')
    create_tre(iseg2)

    create_text_segment(f2)

    create_des(f2, q = 0.2)

    f.write("basic_nitf.ntf")
    f2.write("basic2_nitf.ntf")

    logger = logging.getLogger("nitf_diff")
    # This doesn't seem to have the desired effect, so I created
    # pytest.ini to set the logging level - wlb
    logging.basicConfig(level=logging.DEBUG)

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf") == False

def test_nitf_diff_image_segment_value_tolerance(config_dir):
    f = NitfFile()
    iseg = create_image_seg(f, iid1='An IID1')
    create_tre(iseg)

    f2 = NitfFile()
    iseg2 = create_image_seg(f2, iid1='An IID1', num=10)
    create_tre(iseg2)

    f.write("basic_nitf.ntf")
    f2.write("basic2_nitf.ntf")

    logger = logging.getLogger("nitf_diff")
    # This doesn't seem to have the desired effect, so I created
    # pytest.ini to set the logging level - wlb
    logging.basicConfig(level=logging.DEBUG)

    configFile = config_dir.join("nitf_diff_histogram_tolerance.json")
    with open(configFile) as json_file:
        configData = json.load(configFile)

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf", config=configData) == True

def test_nitf_diff_image_segment_count_tolerance(config_dir):
    f = NitfFile()
    iseg = create_image_seg(f, iid1='An IID1')
    create_tre(iseg)

    f2 = NitfFile()
    iseg2 = create_image_seg(f2, iid1='An IID1', adjust=[(1, 2, 3)])
    create_tre(iseg2)

    f.write("basic_nitf.ntf")
    f2.write("basic2_nitf.ntf")

    logger = logging.getLogger("nitf_diff")
    # This doesn't seem to have the desired effect, so I created
    # pytest.ini to set the logging level - wlb
    logging.basicConfig(level=logging.DEBUG)

    configFile = config_dir.join("nitf_diff_count_tolerance.json")
    with open(configFile) as json_file:
        configData = json.load(configFile)

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf", config=configData) == True

def test_nitf_diff_image_segment_histogram_tolerance(config_dir):
    f = NitfFile()
    iseg = create_image_seg(f, iid1='An IID1')
    create_tre(iseg)

    f2 = NitfFile()
    iseg2 = create_image_seg(f2, iid1='An IID1', num=100)
    create_tre(iseg2)

    f.write("basic_nitf.ntf")
    f2.write("basic2_nitf.ntf")

    logger = logging.getLogger("nitf_diff")
    # This doesn't seem to have the desired effect, so I created
    # pytest.ini to set the logging level - wlb
    logging.basicConfig(level=logging.DEBUG)

    configFile = config_dir.join("nitf_diff_histogram_tolerance.json")
    with open(configFile) as json_file:
        configData = json.load(configFile)

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf", config=configData) == False

def test_nitf_diff_image_segment_histogram_tolerance2(config_dir):
    f = NitfFile()
    iseg = create_image_seg(f, iid1='An IID1', adjust=[(1, 2, 200)])
    create_tre(iseg)

    f2 = NitfFile()
    iseg2 = create_image_seg(f2, iid1='An IID1', adjust=[(1, 2, 200), (1, 3, 201), (1, 4, 202)])
    create_tre(iseg2)

    f.write("basic_nitf.ntf")
    f2.write("basic2_nitf.ntf")

    logger = logging.getLogger("nitf_diff")
    # This doesn't seem to have the desired effect, so I created
    # pytest.ini to set the logging level - wlb
    logging.basicConfig(level=logging.DEBUG)

    configFile = config_dir.join("nitf_diff_histogram_tolerance.json")
    with open(configFile) as json_file:
        configData = json.load(configFile)

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf", config=configData) == True

def test_image_content(isolated_dir):
    '''This create an end to end NITF file, this was at least initially the
    same as basic_nitf_example.py but as a unit test.'''

    # Create the file. We don't supply a name yet, that comes when we actually
    # write

    f = create_basic_nitf()

    iseg = create_image_seg(f, num=9)
    create_tre(iseg)


    f2 = create_basic_nitf()
    # This exercises the nitf_image_subheader eq_string_ignore_case function used by the iid1 field.
    iseg2 = create_image_seg(f2)
    create_tre(iseg2)

    f.write("basic_nitf.ntf")
    f2.write("basic2_nitf.ntf")

    logger = logging.getLogger("nitf_diff")
    # This doesn't seem to have the desired effect, so I created
    # pytest.ini to set the logging level - wlb
    logging.basicConfig(level=logging.DEBUG)

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf") == False

def test_EXT_DEF_CONTENT_eq(isolated_dir):
    # -- File 1 --

    f = create_basic_nitf()
    d = DesEXT_h5()
    h_f = h5py.File("mytestfile.hdf5", "w")
    h_f['abc']=456
    h_f.close()
    d.attach_file("mytestfile.hdf5")
    de3 = NitfDesSegment(des=d)
    f.des_segment.append(de3)
    f.write("basic_nitf.ntf")

    # -- File 2 --
    f2 = create_basic_nitf()
    d = DesEXT_h5()
    d.attach_file("mytestfile.hdf5")
    de3 = NitfDesSegment(des=d)
    f2.des_segment.append(de3)
    f2.write("basic2_nitf.ntf")

    logger = logging.getLogger("nitf_diff")
    # This doesn't seem to have the desired effect, so I created
    # pytest.ini to set the logging level - wlb
    logging.basicConfig(level=logging.DEBUG)

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf") == True


def test_EXT_DEF_CONTENT_ne(isolated_dir):
    # -- File 1 --

    f = create_basic_nitf()
    d = DesEXT_h5()
    h_f = h5py.File("mytestfile.hdf5", "w")
    h_f['abc']=456
    h_f.close()
    d.attach_file("mytestfile.hdf5")
    de3 = NitfDesSegment(des=d)
    f.des_segment.append(de3)
    f.write("basic_nitf.ntf")

    # -- File 2 --
    f2 = create_basic_nitf()
    d = DesEXT_h5()
    h_f = h5py.File("mytestfile.hdf5", "w")
    h_f['abc'] = 457
    h_f.close()
    d.attach_file("mytestfile.hdf5")
    de3 = NitfDesSegment(des=d)
    f2.des_segment.append(de3)
    f2.write("basic2_nitf.ntf")

    logger = logging.getLogger("nitf_diff")
    # This doesn't seem to have the desired effect, so I created
    # pytest.ini to set the logging level - wlb
    logging.basicConfig(level=logging.DEBUG)

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf") == False