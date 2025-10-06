import pytest
from pathlib import Path
import os
import sys

# Add source to path. For some reason pytest can miss this even if we
# have this installed editable with a --prefix pip install (probably
# some weird PYTHONPATH interaction not worth tracking down when we can
# just work around it).
sys.path.append(str(Path(os.path.dirname(__file__)).parent))

# Short hand for marking as unconditional skipping. Good for tests we
# don't normally run, but might want to comment out for a specific debugging
# reason.
skip = pytest.mark.skip

# ------------------------------------------
# Includes fixtures, made available to all tests.
# ------------------------------------------

pytest_plugins = [
    "fixtures.dir_fixture",
    "fixtures.misc_fixture",
]
