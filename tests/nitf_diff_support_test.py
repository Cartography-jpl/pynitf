import subprocess
import os
import json
import numpy as np
import logging
from pynitf import *
from pynitf_test_support import *

#********************************************************
# NOTE! This code is all being replaced with a reorganization
# of NitfDiff. Left in place here until we get all the
# functionality moved over
#********************************************************

def create_basic_nitf():
    f = NitfFile()
    create_tre(f)
    create_tre(f, 290)
    create_text_segment(f)
    return f

def test_nitf_diff_neq_one_val(isolated_dir):
    f = NitfFile()
    create_tre(f)
    f.write("basic_nitf.ntf")

    f = NitfFile()
    create_tre(f, 290)
    f.write("basic2_nitf.ntf")

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf") == False

# TODO Need to fix this functionality, and move to the new structure
@skip    
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
    iseg2 = create_image_seg(f2, iid1='an iid1')
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

    create_tre(f, 290)

    iseg = create_image_seg(f, iid1='An IID1')
    # create_tre(iseg, atn = 43)
    create_tre(iseg)

    create_text_segment(f)

    # Using the alternate desid of to break the diff, as it should.
    create_des(f)
    # create_des(f)

    f2 = NitfFile()
    create_tre(f2)
    create_tre(f2, 290)
    # This exercises the nitf_image_subheader eq_string_ignore_case function used by the iid1 field.
    iseg2 = create_image_seg(f2, iid1='an iid1')
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
    iseg2 = create_image_seg(f2, iid1='An IID1', row_offset=10)
    create_tre(iseg2)

    f.write("basic_nitf.ntf")
    f2.write("basic2_nitf.ntf")

    logger = logging.getLogger("nitf_diff")
    # This doesn't seem to have the desired effect, so I created
    # pytest.ini to set the logging level - wlb
    logging.basicConfig(level=logging.DEBUG)

    with open("nitf_diff_histogram_tolerance.json") as fh:
        config_data = json.load(fh)

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf",
                          config=config_data) == True

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

    with open("nitf_diff_count_tolerance.json") as fh:
        config_data = json.load(fh)

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf",
                          config=config_data) == True

def test_nitf_diff_image_segment_histogram_tolerance(config_dir):
    f = NitfFile()
    iseg = create_image_seg(f, iid1='An IID1')
    create_tre(iseg)

    f2 = NitfFile()
    iseg2 = create_image_seg(f2, iid1='An IID1', row_offset=100)
    create_tre(iseg2)

    f.write("basic_nitf.ntf")
    f2.write("basic2_nitf.ntf")

    logger = logging.getLogger("nitf_diff")
    # This doesn't seem to have the desired effect, so I created
    # pytest.ini to set the logging level - wlb
    logging.basicConfig(level=logging.DEBUG)

    with open("nitf_diff_histogram_tolerance.json") as fh:
        config_data = json.load(fh)
    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf",
                          config=config_data) == False

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

    with open("nitf_diff_histogram_tolerance.json") as fh:
        config_data = json.load(fh)

    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf",
                          config=config_data) == True

def test_image_content(isolated_dir):
    '''This create an end to end NITF file, this was at least initially the
    same as basic_nitf_example.py but as a unit test.'''

    # Create the file. We don't supply a name yet, that comes when we actually
    # write

    f = create_basic_nitf()

    iseg = create_image_seg(f, row_offset=9)
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
