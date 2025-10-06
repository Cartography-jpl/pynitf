# This defines fixtures that gives the paths to various directories with
# test data

import os
import pytest
from pathlib import Path


@pytest.fixture(scope="function")
def unit_test_data():
    """Return the unit test directory"""
    return Path(os.path.dirname(__file__)).parent / "unit_test_data"


@pytest.fixture(scope="function")
def xsd_dir():
    """Return the XSD directory"""
    return Path(os.path.dirname(__file__)).parent.parent / "xsd"


@pytest.fixture(scope="function")
def program_dir():
    """Return the location of the programs"""
    return Path(os.path.dirname(__file__)).parent.parent / "bin"
