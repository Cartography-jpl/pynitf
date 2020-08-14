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

def test_nitf_diff(isolated_dir):
    f = NitfFile()
    create_tre(f)
    f.write("basic_nitf.ntf")
    f = NitfFile()
    create_tre(f, 290)
    f.write("basic2_nitf.ntf")
    print("Results of nitf_diff, should be different.")
    t = subprocess.run(["nitf_diff", "basic_nitf.ntf",
                        "basic2_nitf.ntf"])
    assert t.returncode == 1
    print("Results of nitf_diff, should be different. Generates log file")
    t = subprocess.run(["nitf_diff", "--log-file=nitf_diff.log1",
                        "basic_nitf.ntf",
                        "basic2_nitf.ntf"])
    assert t.returncode == 1
    print("Results of nitf_diff. Generates log file only")
    t = subprocess.run(["nitf_diff", "--log-file-only=nitf_diff.log2",
                        "basic_nitf.ntf",
                        "basic2_nitf.ntf"])
    assert t.returncode == 1
    print("Results of nitf_diff, should have warnings but not different.")
    t = subprocess.run(["nitf_diff",
                        "--config-file-python=" + unit_test_data +
                        "sample_nitf_diff_config.py",
                        "basic_nitf.ntf",
                        "basic2_nitf.ntf"])
    assert t.returncode == 0

def test_special_eq_diff(isolated_dir):
    '''Do a comparison where we supply an explict eq function. In this
    case we compare the first file field to a fixed value, ignoring the 
    second files field value. This is useful for example where
    we have an existing expected results that hasn't been updated yet,
    and we want to ignore the change for now. This would likely be a
    temporary sort of configuration (e.g., focus on other parts of the
    file until we are ready to update the expected values)'''
    f = NitfFile()
    create_tre(f)
    f.tre_list[0].rev_num = 3200
    f.write("nitf1.ntf")
    f = NitfFile()
    create_tre(f)
    f.write("nitf2.ntf")
    print("Results of nitf_diff, should be different")
    t = subprocess.run(["nitf_diff", "nitf1.ntf",
                        "nitf2.ntf"])
    assert t.returncode == 1

    print("Results of nitf_diff, should be same")
    t = subprocess.run(["nitf_diff",
                        "--config-file-python=" + unit_test_data +
                        "sample_nitf_diff_config2.py",
                        "nitf1.ntf",
                        "nitf2.ntf"])
    assert t.returncode == 0
    

@require_h5py    
def test_nitf_diff_h5py(isolated_dir):
    '''Add h5py file'''
    h = h5py.File("test.h5", "w")
    g = h.create_group("TestGroup")
    g.create_dataset("test_data", data=b"hi there",
                     dtype=h5py.special_dtype(vlen=bytes))
    h.close()

    h = h5py.File("test2.h5", "w")
    g = h.create_group("TestGroup")
    g.create_dataset("test_data", data=b"hi there, this is different",
                     dtype=h5py.special_dtype(vlen=bytes))
    h.close()

    f = NitfFile()
    create_tre(f)
    d = DesEXT_h5(file="test.h5")
    d.user_subheader.content_description = b"hi there"
    f.des_segment.append(NitfDesSegment(d))
    f.write("nitf1.ntf")

    f = NitfFile()
    create_tre(f)
    d = DesEXT_h5(file="test2.h5")
    d.user_subheader.content_description = b"hi there"
    f.des_segment.append(NitfDesSegment(d))
    f.write("nitf2.ntf")
    
    print("Results of nitf_diff, should be same")
    t = subprocess.run(["nitf_diff", "nitf1.ntf",
                        "nitf1.ntf"])
    assert t.returncode == 0

    print("Results of nitf_diff, should be different")
    t = subprocess.run(["nitf_diff", "nitf1.ntf",
                        "nitf2.ntf"])
    assert t.returncode == 1

    print("Results of nitf_diff, should have warnings, but not be different")
    t = subprocess.run(["nitf_diff",
                        "--config-file-python=" + unit_test_data +
                        "sample_nitf_diff_config.py",
                        "nitf1.ntf",
                        "nitf2.ntf"])
    assert t.returncode == 0
    
def test_extra_tre(isolated_dir):
    '''Test have an extra TRE in the first file. This would be for example
    if we have extended a file and want to compare against an expected value
    w/o yet worrying about the new TRE. Like the test_special_eq_diff is 
    would likely be a temporary thing before we are ready to update 
    some expected results.'''

    f = NitfFile()
    t = TreSTDIDC()
    f.tre_list.append(t)
    create_tre(f)
    f.write("nitf1.ntf")
    f = NitfFile()
    create_tre(f)
    f.write("nitf2.ntf")
    print("Results of nitf_diff, should be different")
    t = subprocess.run(["nitf_diff", "nitf1.ntf",
                        "nitf2.ntf"])
    assert t.returncode == 1

    print("Results of nitf_diff, should be same")
    t = subprocess.run(["nitf_diff",
                        "--config-file-python=" + unit_test_data +
                        "sample_nitf_diff_config.py",
                        "nitf1.ntf",
                        "nitf2.ntf"])
    assert t.returncode == 0
    
