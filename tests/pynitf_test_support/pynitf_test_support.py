# This contains support routines for unit tests.
import numpy as np
from numpy.testing import assert_almost_equal, assert_approx_equal
from pynitf.nitf_security import NitfSecurity
from pynitf.nitf_image import NitfImageWriteNumpy
from pynitf.nitf_file import (NitfImageSegment, NitfTextSegment,
                              NitfDesSegment, NitfGraphicSegment,
                              NitfResSegment)
from pynitf.nitf_text import NitfTextStr
from pynitf.nitf_segment_data_handle import NitfGraphicRaw, NitfResRaw
from pynitf.nitf_des_csattb import DesCSATTB
from pynitf.nitf_tre_csde import TreUSE00A
from pynitf.nitf_tre import TreWarning
from pynitf.nitf_diff_handle import DifferenceFormatter
from unittest import SkipTest
import os
import sys
import subprocess
import re
import math
from distutils import dir_util
import json
import pytest
import logging
import warnings

# Some unit tests require h5py. This is not an overall requirement, so if
# not found we just skip those tests
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import h5py
    have_h5py = True
except ImportError:
    # Ok if we don't have h5py, we just can't execute this code
    have_h5py = False

# All warnings about TREs are treated as errors.
#
# With the exception:
# The MATESA TRE changed between v 0.1 and 1.0 of the SNIP. The RIP
# data uses the old format. We can't do anything about this, so just
# ignore warning messages about this TRE. But treat other warnings as
# errors

pytestmark = [pytest.mark.filterwarnings("error::pynitf.TreWarning"),
              pytest.mark.filterwarnings("ignore:Trouble reading TRE MATESA:pynitf.TreWarning")]

# Location of test data that is part of source
unit_test_data = os.path.abspath(os.path.expandvars(os.path.dirname(__file__)) + "/unit_test_data/") + "/"
# Locate of programs
program_dir = os.path.abspath(os.path.expandvars(os.path.dirname(__file__)) + "../../../bin/") + "/"
os.environ["PATH"] = program_dir + ":" + os.environ["PATH"]

# Fake security object, just so we can test setting and reading
security_fake = NitfSecurity()
security_fake.classification = "T"
security_fake.classification_system = "US"
security_fake.codewords = "BOO"
security_fake.control_and_handling = "UO"
security_fake.release_instructions = "US UG"
security_fake.declassification_type = "DD"
security_fake.declassification_date = "30000101"
security_fake.declassification_exemption = "X251"
security_fake.downgrade =  "S"
security_fake.downgrade_date = "25000101"
security_fake.classification_text = "Fake classification"
security_fake.classification_authority_type = "D"
security_fake.classification_authority = "X-File"
security_fake.classification_reason = "X"
security_fake.security_source_date = "19000101"
security_fake.security_control_number = "1234"
security_fake.copy_number = 2
security_fake.number_of_copies = 5
security_fake.encryption = 1

# We often have errors in formatting floats. Give a few "evil" floats to
# use in testing
evil_float1 = math.pi
evil_float2 = math.pi * 1e-12
evil_float3 = math.pi * 1e+12


# Short hand for marking as unconditional skipping. Good for tests we
# don't normally run, but might want to comment out for a specific debugging
# reason.
skip = pytest.mark.skip

def cmd_exists(cmd):
    '''Check if a cmd exists by using type, which returns a nonzero status if
    the program isn't found'''
    return subprocess.call("type " + cmd, shell=True, 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def create_image_seg(f, security = None, iid1 = '', row_offset = 10, bias = 0,
                     adjust = None, nrow = 9, ncol = 10):
    '''Create a small image segment. The security setting can be passed in,
    otherwise the default unclassified version is used. The IID can be passed.
    The values filled in can be controlled by row_offset, bias, and adjust.'''
    img = NitfImageWriteNumpy(nrow, ncol, np.uint8)
    for i in range(nrow):
        for j in range(ncol):
            img[0, i, j] = i * row_offset + j
    iseg = NitfImageSegment(img, security=security)
    iseg.iid1 = iid1
    f.image_segment.append(iseg)
    return iseg

def create_tre(f, angle_to_north = 270):
    '''Create a sample TRE. We use TreUSE00A because it is a simple TRE. You
    can pass in different values to angle_to_north to get "different" TREs.
    '''
    t = TreUSE00A()
    t.angle_to_north = angle_to_north
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

def create_text_segment(f, first_name = 'Guido', textid = 'ID12345',
                        security = None):
    '''Create a text segment'''
    d = {
        'first_name': first_name,
        'second_name': 'Rossum',
        'titles': ['BDFL', 'Developer'],
    }
    ts = NitfTextSegment(NitfTextStr(json.dumps(d)), security=security)
    ts.subheader.textid = textid
    ts.subheader.txtalvl = 0
    ts.subheader.txtitl = 'sample title'
    f.text_segment.append(ts)

def create_graphic_segment(f, graphic_data=b'fake graph data',
                           graphicid = 'GID12345', security = None):
    '''Create a graphic segment'''
    gs = NitfGraphicSegment(NitfGraphicRaw(graphic_data),
                            security=security)
    gs.subheader.sid = graphicid
    gs.subheader.sname = "Fake graphic"
    gs.subheader.salvl = 0
    f.graphic_segment.append(gs)

def create_res_segment(f, res_data=b'fake res data',
                       resid = 'GID12345', security = None):
    '''Create a res segment'''
    rs = NitfResSegment(NitfResRaw(res_data), security=security)
    rs.subheader.resid = resid
    f.res_segment.append(rs)
    
def create_des(f, date_att = 20170501, q = 0.1, security=None):
    '''Create a DES segment'''
    des = DesCSATTB()
    ds = des.user_subheader
    ds.id = '4385ab47-f3ba-40b7-9520-13d6b7a7f311'
    ds.numais = '010'
    for i in range(int(ds.numais)):
        ds.aisdlvl[i] = 5 + i
    ds.reservedsubh_len = 0

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

    de = NitfDesSegment(des, security=security)
    f.des_segment.append(de)
    
    
# Some tests are python 3 only. Don't want the python 2 tests to fail for
# python code that we know can't be run
require_python3 = pytest.mark.skipif(not sys.version_info > (3,),
       reason = "require python 3 to run")                                     

def gdal_value(f, line, sample, band = None):
    '''Return value at the given location, according to gdal. This is 
    return as a bytes, which you can then cast to the desired type
    (e.g., int())'''
    cmd = ["gdallocationinfo", "-valonly"]
    if(band is not None):
        cmd.extend(["-b", str(band + 1)])
    cmd.extend([f, str(sample), str(line)])
    res = subprocess.run(cmd, check=True,stdout=subprocess.PIPE).stdout
    # Complex numbers need special handling, because gdallocationinfo doesn't
    # write a string that python knows how to parse.
    if(b'+' in res or b'i' in res):
        res = (b'(' + re.sub(b'i', b'j', res.rstrip()) + b')\n').decode('utf-8')
    return res

require_gdal_value = pytest.mark.skipif(not sys.version_info > (3,) or
                   not cmd_exists("gdallocationinfo"),
                   reason="Require python 3 and gdallocationinfo")

@pytest.yield_fixture(scope="function")
def print_logging(isolated_dir):
    '''Direct logging to a local "run.log" file.

    Also print the logger to the console. Normally this only shows up for
    failed tasks, but with -s we print this out for each job that runs.
    '''
    h = logging.FileHandler('run.log')
    h.setLevel(logging.INFO)
    h.setFormatter(DifferenceFormatter())
    logger = logging.getLogger('nitf_diff')
    original_lv = logger.getEffectiveLevel()
    try:
        logger.setLevel(logging.INFO)
        logger.addHandler(h)
        yield
    finally:
        logger.setLevel(original_lv)
        logger.removeHandler(h)
    # We output the run.log file rather than just attaching the logger to
    # the console so we can avoid the "Logger output:" part if there is no
    # actual output.
    t = open("run.log").read()
    if(len(t) > 0):
        print("\nLogger output:")
        print(t)

@pytest.yield_fixture(scope="function")
def config_dir(tmpdir, request):
    '''
    Likes isolated_dir, but first copies a folder with the same name of test
    module and, if available, moves all contents to the temporary directory so
    tests can use them freely.
    '''
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))
    curdir = os.getcwd()
    try:
        tmpdir.chdir()
        yield curdir
    finally:
        os.chdir(curdir)

@pytest.yield_fixture(scope="function")
def isolated_dir(tmpdir):
    '''This is a fixture that creates a temporary directory, and uses this
    while running a unit tests. Useful for tests that write out a test file
    and then try to read it.

    This fixture changes into the temporary directory, and at the end of
    the test it changes back to the current directory.

    Note that this uses the fixture tmpdir, which keeps around the last few
    temporary directories (cleaning up after a fixed number are generated).
    So if a test fails, you can look at the output at the location of tmpdir, 
    e.g. /tmp/pytest-of-smyth
    '''
    curdir = os.getcwd()
    try:
        tmpdir.chdir()
        yield curdir
    finally:
        os.chdir(curdir)

# Have tests that require NITF sample files be available. We skip these if not
# available, tests are nice to make sure things don't break but not essential.
# Things that really matter have small test data sets put into unit_test_data,
# but we do want the option of running larger tests when available

@pytest.yield_fixture(scope="function")
def nitf_sample_files(isolated_dir):
    if(os.path.exists("/bigdata/smyth/NitfSamples/")):
        return "/bigdata/smyth/NitfSamples/"
    elif(os.path.exists("/opt/nitf_files/NitfSamples/")):
        return "/opt/nitf_files/NitfSamples/"
    elif(os.path.exists("/data2/smythdata/NitfSamples/")):
        return "/data2/smythdata/NitfSamples/"
    elif(os.path.exists("/data2/smythdata/NitfSamples/")):
        return "/data2/smythdata/NitfSamples/"
    elif(os.path.exists("/Users/smyth/NitfSamples/")):
        return "/Users/smyth/NitfSamples/"
    pytest.skip("Require NitfSamples test data to run")

@pytest.yield_fixture(scope="function")
def nitf_sample_quickbird(nitf_sample_files):
    fname = nitf_sample_files + "quickbird/05NOV23034644-P1BS-005545406180_01_P001.NTF"
    if(os.path.exists(fname)):
        return fname
    pytest.skip("Required file %s not found, so skipping test" % fname)

@pytest.yield_fixture(scope="function")
def nitf_sample_wv2(nitf_sample_files):
    fname = nitf_sample_files + "wv2/12JAN23015358-P1BS-052654848010_01_P003.NTF"
    if(os.path.exists(fname)):
        return fname
    pytest.skip("Required file %s not found, so skipping test" % fname)

@pytest.yield_fixture(scope="function")
def nitf_sample_ikonos(nitf_sample_files):
    fname = nitf_sample_files + "ikonos/11DEC11IK0101000po_755166_pan_0000000.ntf"
    if(os.path.exists(fname)):
        return fname
    pytest.skip("Required file %s not found, so skipping test" % fname)

@pytest.yield_fixture(scope="function")
def nitf_sample_rip(nitf_sample_files):
    fname = nitf_sample_files + "rip/07APR2005_Hyperion_331405N0442002E_SWIR172_001_L1R.ntf"
    if(os.path.exists(fname)):
        return fname
    pytest.skip("Required file %s not found, so skipping test" % fname)
    
require_h5py = pytest.mark.skipif(not have_h5py,
      reason="need to have h5py available to run.")
