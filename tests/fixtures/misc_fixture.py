# Fixtures that don't really fit in one of the other files.
from pynitf import NitfSecurity, DifferenceFormatter
import pytest
import os
import math
import logging


@pytest.fixture(scope="function")
def isolated_dir(tmpdir):
    """This is a fixture that creates a temporary directory, and uses this
    while running a unit tests. Useful for tests that write out a test file
    and then try to read it.

    This fixture changes into the temporary directory, and at the end of
    the test it changes back to the current directory.

    Note that this uses the fixture tmpdir, which keeps around the last few
    temporary directories (cleaning up after a fixed number are generated).
    So if a test fails, you can look at the output at the location of tmpdir,
    e.g. /tmp/pytest-of-smyth
    """
    curdir = os.getcwd()
    try:
        tmpdir.chdir()
        yield curdir
    finally:
        os.chdir(curdir)


@pytest.fixture(scope="function")
def print_logging(isolated_dir):
    """Direct logging to a local "run.log" file.

    Also print the logger to the console. Normally this only shows up for
    failed tasks, but with -s we print this out for each job that runs.
    """
    h = logging.FileHandler("run.log")
    h.setLevel(logging.INFO)
    h.setFormatter(DifferenceFormatter())
    logger = logging.getLogger("nitf_diff")
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
    if len(t) > 0:
        print("\nLogger output:")
        print(t)


@pytest.fixture(scope="function")
def evil_float1():
    """We often have errors in formatting floats. Give a few "evil" floats to
    use in testing"""
    return math.pi


@pytest.fixture(scope="function")
def evil_float2():
    """We often have errors in formatting floats. Give a few "evil" floats to
    use in testing"""
    return math.pi * 1e-12


@pytest.fixture(scope="function")
def evil_float3():
    """We often have errors in formatting floats. Give a few "evil" floats to
    use in testing"""
    return math.pi * 1e12


@pytest.fixture(scope="function")
def security_fake():
    # Fake security object, just so we can test setting and reading
    res = NitfSecurity()
    res.classification = "T"
    res.classification_system = "US"
    res.codewords = "BOO"
    res.control_and_handling = "UO"
    res.release_instructions = "US UG"
    res.declassification_type = "DD"
    res.declassification_date = "30000101"
    res.declassification_exemption = "X251"
    res.downgrade = "S"
    res.downgrade_date = "25000101"
    res.classification_text = "Fake classification"
    res.classification_authority_type = "D"
    res.classification_authority = "X-File"
    res.classification_reason = "X"
    res.security_source_date = "19000101"
    res.security_control_number = "1234"
    res.copy_number = 0
    res.number_of_copies = 0
    res.encryption = 1
    return res


# Have tests that require NITF sample files be available. We skip these if not
# available, tests are nice to make sure things don't break but not essential.
# Things that really matter have small test data sets put into unit_test_data,
# but we do want the option of running larger tests when available


@pytest.fixture(scope="function")
def nitf_sample_files(isolated_dir):
    if os.path.exists("/bigdata/smyth/NitfSamples/"):
        return "/bigdata/smyth/NitfSamples/"
    elif os.path.exists("/opt/nitf_files/NitfSamples/"):
        return "/opt/nitf_files/NitfSamples/"
    elif os.path.exists("/data2/smythdata/NitfSamples/"):
        return "/data2/smythdata/NitfSamples/"
    elif os.path.exists("/data2/smythdata/NitfSamples/"):
        return "/data2/smythdata/NitfSamples/"
    elif os.path.exists("/Users/smyth/NitfSamples/"):
        return "/Users/smyth/NitfSamples/"
    pytest.skip("Require NitfSamples test data to run")


@pytest.fixture(scope="function")
def nitf_sample_quickbird(nitf_sample_files):
    fname = nitf_sample_files + "quickbird/05NOV23034644-P1BS-005545406180_01_P001.NTF"
    if os.path.exists(fname):
        return fname
    pytest.skip("Required file %s not found, so skipping test" % fname)


@pytest.fixture(scope="function")
def nitf_sample_wv2(nitf_sample_files):
    fname = nitf_sample_files + "wv2/12JAN23015358-P1BS-052654848010_01_P003.NTF"
    if os.path.exists(fname):
        return fname
    pytest.skip("Required file %s not found, so skipping test" % fname)


@pytest.fixture(scope="function")
def nitf_sample_ikonos(nitf_sample_files):
    fname = nitf_sample_files + "ikonos/11DEC11IK0101000po_755166_pan_0000000.ntf"
    if os.path.exists(fname):
        return fname
    pytest.skip("Required file %s not found, so skipping test" % fname)


@pytest.fixture(scope="function")
def nitf_sample_rip(nitf_sample_files):
    fname = (
        nitf_sample_files + "rip/07APR2005_Hyperion_331405N0442002E_SWIR172_001_L1R.ntf"
    )
    if not os.path.exists(fname):
        pytest.skip("Required file %s not found, so skipping test" % fname)
    return fname
