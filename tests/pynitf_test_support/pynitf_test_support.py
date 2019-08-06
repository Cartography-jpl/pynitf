# This contains support routines for unit tests.
import numpy as np
from numpy.testing import assert_almost_equal, assert_approx_equal
from unittest import SkipTest
import os
import sys
import subprocess
import re
import pytest
# Some unit tests require h5py. This is not an overall requirement, so if
# not found we just skip those tests
try:
    import h5py
    have_h5py = True
except ImportError:
    # Ok if we don't have h5py, we just can't execute this code
    have_h5py = False

# Location of test data that is part of source
unit_test_data = os.path.abspath(os.path.dirname(__file__) + "/unit_test_data/") + "/"

# Short hand for marking as unconditional skipping. Good for tests we
# don't normally run, but might want to comment out for a specific debugging
# reason.
skip = pytest.mark.skip

def cmd_exists(cmd):
    '''Check if a cmd exists by using type, which returns a nonzero status if
    the program isn't found'''
    return subprocess.call("type " + cmd, shell=True, 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

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
    if(os.path.exists("/raid1/smyth/NitfSamples/")):
        return "/raid1/smyth/NitfSamples/"
    elif(os.path.exists("/opt/nitf_files/NitfSamples/")):
        return "/opt/nitf_files/NitfSamples/"
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
