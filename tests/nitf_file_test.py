import cProfile
from pynitf.nitf_file import NitfFile
from pynitf.nitf_tre import Tre, tre_tag_to_cls
from pynitf_test_support import *
import pynitf.nitf_field
import pynitf.nitf_des
import subprocess
import os
import json
import numpy as np
import filecmp
import gc

# Turn on debug messages
#pynitf.nitf_field.DEBUG = True
#pynitf.nitf_des.DEBUG = True
    
def check_tre(t, angle_to_north = 270):    
    assert t.tre_tag == "USE00A"
    assert t.angle_to_north == angle_to_north
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
    create_tre(f.image_segment[0], 290)
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
    check_tre(f2.image_segment[0].tre_list[0], 290)
    print_diag(f2)

def test_large_tre_write(isolated_dir):
    '''Repeat of test_basic_write, but also include a really big TRE that
    forces the use of the second place in the header for TREs'''
    class TreBig(Tre):
        desc = [["big_field", "", 99999-20, str],]
        tre_tag = "BIGTRE"
    tre_tag_to_cls.add_cls(TreBig)    
    f = NitfFile()
    create_image_seg(f)
    f.tre_list.append(TreBig())
    f.image_segment[0].tre_list.append(TreBig())
    create_tre(f)
    create_tre(f.image_segment[0], 290)
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
    check_tre([tre for tre in f2.image_segment[0].tre_list if tre.tre_tag == "USE00A"][0], 290)
    check_tre([tre for tre in f3.image_segment[0].tre_list if tre.tre_tag == "USE00A"][0], 290)
    print_diag(f2)
    print_diag(f3)
    assert filecmp.cmp("z.ntf", "z2.ntf", shallow=False)
    
def test_tre_overflow_write(isolated_dir):
    '''Repeat of test_basic_write, but also include two really big TREs that
    forces the use of the DES TRE overflow for TREs'''
    class TreBig(Tre):
        desc = [["big_field", "", 99999-20, str]]
        tre_tag = "BIGTRE"
    tre_tag_to_cls.add_cls(TreBig)    
    f = NitfFile()
    create_image_seg(f)
    f.tre_list.append(TreBig())
    f.tre_list.append(TreBig())
    f.image_segment[0].tre_list.append(TreBig())
    f.image_segment[0].tre_list.append(TreBig())
    create_tre(f)
    create_tre(f.image_segment[0], 290)
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
    check_tre([tre for tre in f2.image_segment[0].tre_list if tre.tre_tag == "USE00A"][0], 290)
    check_tre([tre for tre in f3.image_segment[0].tre_list if tre.tre_tag == "USE00A"][0], 290)
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
    f = NitfFile()
    f.data_handle_set.add_handle(pynitf.NitfDesCopy, priority_order=-999)
    f.read(nitf_sample_wv2)
    original_output = str(f)
    fname_copy = "worldview_copy.ntf"
    f.write(fname_copy)
    f2 = NitfFile()
    f2.data_handle_set.add_handle(pynitf.NitfDesCopy, priority_order=-999)
    f2.read(fname_copy)
    copy_output = str(f2)
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
    '''Test copying a RIP NITF file. It creates a copy of the file and
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
    create_tre(f, 290)
    create_text_segment(f)
    create_des(f)
    create_graphic_segment(f)
    create_res_segment(f)
    print(f)
    f.write("basic_nitf.ntf")
    f2 = NitfFile()
    f2.data_handle_set.add_handle(NitfGraphicRaw)
    f2.data_handle_set.add_handle(NitfResRaw)
    f2.read("basic_nitf.ntf")
    print(f2)
    print("Image Data:")
    print(f2.image_segment[0].data.data)

    print("Text Data:")
    print(f2.text_segment[0].data)        

    print("Graphic Data:")
    print(f2.graphic_segment[0].data)        

    print("Res Data:")
    print(f2.res_segment[0].data)        
    
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
    create_tre(f, 290)
    create_text_segment(f, security=security_fake)
    create_des(f, security=security_fake)
    create_graphic_segment(f, security=security_fake)
    create_res_segment(f, security=security_fake)
    print(f)
    f.write("basic_nitf.ntf")
    f2 = NitfFile()
    f2.data_handle_set.add_handle(NitfGraphicRaw)
    f2.data_handle_set.add_handle(NitfResRaw)
    f2.read("basic_nitf.ntf")
    print("Image Data:")
    print(f2.image_segment[0].data.data)

    print("Text Data:")
    print(f2.text_segment[0].data)        

    print("Graphic Data:")
    print(f2.graphic_segment[0].data)        

    print("Res Data:")
    print(f2.res_segment[0].data)        
    
# This is a set of sample NITF files found at
# https://gwg.nga.mil/ntb/baseline/software/testfile/Nitfv2_1/scen_2_1.html.
# Go through an make sure we can read them all (as a minimum check)
flist = ["i_3001a.ntf", "i_3004g.ntf", "i_3008a.ntf", "i_3015a.ntf",
         "i_3018a.ntf", "i_3025b.ntf", "i_3034c.ntf", "i_3034f.ntf",
         "i_3041a.ntf", "i_3051e.ntf", "i_3052a.ntf", "i_3060a.ntf",
         "i_3063f.ntf", "i_3068a.ntf", "i_3076a.ntf", "i_3090m.ntf",
         "i_3090u.ntf", "i_3113g.ntf", "i_3114e.ntf", "i_3117ax.ntf",
         "i_3128b.ntf", "i_3201c.ntf", "i_3228c.ntf", "i_3228e.ntf",
         "i_3301a.ntf", "i_3301c.ntf", "i_3301h.ntf", "i_3301k.ntf",
         "i_3303a.ntf", "i_3309a.ntf", "i_3311a.ntf", "i_3405a.ntf",
         "i_3430a.ntf", "i_3450c.ntf", "i_5012c.ntf", "ns3004f.nsf",
         "ns3005b.nsf", "ns3010a.nsf", "ns3017a.nsf", "ns3022b.nsf",
         "ns3033b.nsf", "ns3034d.nsf", "ns3038a.nsf", "ns3050a.nsf",
         "ns3051v.nsf", "ns3059a.nsf", "ns3061a.nsf", "ns3063h.nsf",
         "ns3073a.nsf", "ns3090i.nsf", "ns3090q.nsf", "ns3101b.nsf",
         "ns3114a.nsf", "ns3114i.nsf", "ns3118b.nsf", "ns3119b.nsf",
         "ns3201a.nsf", "ns3228b.nsf", "ns3228d.nsf", "ns3229b.nsf",
         "ns3301b.nsf", "ns3301e.nsf", "ns3301j.nsf", "ns3302a.nsf",
         "ns3304a.nsf", "ns3310a.nsf", "ns3361c.nsf",
         "ns3417c.nsf", "ns3437a.nsf", "ns3450e.nsf", "ns5600a.nsf"]


def test_nitf_sample_nitf(nitf_sample_files):
    for fname in flist:
        f = NitfFile(nitf_sample_files + "/SampleFiles/" + fname)
        print(fname + ":")
        print(f.summary())

# This is a streaming file, which we don't currently support
flist2 = ["ns3321a.nsf",]

# TODO Add support for this
@skip(reason="don't support NITF streaming yet")        
def test_nitf_sample_nitf_streaming(nitf_sample_files):
    for fname in flist2:
        f = NitfFile(nitf_sample_files + "/SampleFiles/" + fname)
        print(fname + ":")
        print(f.summary())
        
# May expand this to check a large file, or we might just separately
# profile reading large files we already have. Can also do
# "python -m cProfile script.py" to test a standalone script
# Can spit into out using:
# python -m cProfile -o prof.dat script.py
# Then things like:
# import pstats
# from pstats import SortKey
# p = pstats.Stats("prof.dat")
# p.sort_stats(SortKey.CUMULATIVE).print_stats(10)
# p.sort_stats(SortKey.TIME).print_stats(10)
# Interactive version with "python -m pstats prof.dat"
@skip(reason="skip profiling by default")
def test_profile(isolated_dir):
    f = NitfFile()
    create_image_seg(f)
    create_tre(f)
    create_tre(f, 290)
    create_text_segment(f)
    create_des(f)
    f.write("basic_nitf.ntf")
    cProfile.run('import pynitf; pynitf.NitfFile("basic_nitf.ntf")')

def test_too_many_file(isolated_dir):
    '''
    Because of how we used np.memmap for images before, we could
    run into "too many files" error if we have a couple of files open
    using large number of images (so more than 1024 images across a 
    few files). 

    We've fixed this by using a single mmap for the entire file.
    This unit test checks this fix by having enough image segments to
    trigger this using the old method.
    '''
    f = NitfFile()
    for i in range(600):
        create_image_seg(f)
    f.write("large_nitf.ntf")
    f1 = NitfFile("large_nitf.ntf")
    f2 = NitfFile("large_nitf.ntf")

def test_gc(isolated_dir):
    '''We have various pieces that reference each other. This can prevent
    reference counting from cleaning up data. The garbage collector will 
    eventually find all these cycles, but it is desirable to just set things 
    up if possible so things get cleaned up right away (since potentially 
    the NitfFile object can be large).'''

    # Create the file. We don't supply a name yet, that comes when we actually
    # write
    
    f = NitfFile()
    create_image_seg(f)
    create_tre(f)
    create_tre(f, 290)
    create_text_segment(f)
    create_des(f)
    f.write("basic_nitf.ntf")
    f2 = NitfFile("basic_nitf.ntf")
    # Clean up whatever happens to be there before this test
    gc.collect()
    # Remove reference to files. Ideally they will then get
    # cleaned up
    f = None
    f2 = None
    # Run gc again with debugging turned on, to see if it finds
    # anything. Ideally there should be nothing
    old_flags = gc.get_debug()
    gc.set_debug(gc.DEBUG_STATS | gc.DEBUG_COLLECTABLE)
    gc.collect()
    gc.set_debug(old_flags)
