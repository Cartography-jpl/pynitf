import subprocess
import os
from pynitf import *
from pynitf_test_support import *


def create_basic_nitf():
    f = NitfFile()
    create_tre(f)
    create_tre(f, 290)
    create_text_segment(f)
    return f

# Haven't gotten nitf_diff working yet, we'll come back to this
#@skip
def test_nitf_diff(isolated_dir):
    f = NitfFile()
    create_tre(f)
    f.write("basic_nitf.ntf")
    f = NitfFile()
    create_tre(f, 290)
    f.write("basic2_nitf.ntf")
    t = subprocess.run([program_dir + "nitf_diff", "basic_nitf.ntf",
                        "basic2_nitf.ntf"])
    assert t.returncode == 1
