from pynitf.nitf_file import NitfFile
from pynitf.nitf_field import NitfLiteral, FieldData
from pynitf.nitf_tre_csde import TreUSE00A
from pynitf.nitf_tre import Tre, tre_tag_to_cls
from pynitf_test_support import *
import copy

@pytest.fixture(scope="function")
def modify_use00a_tre():
    '''Wrapper that allows use00a to be modified and then moved 
    back to normal'''
    try:
        yield
    finally:
        tre_tag_to_cls.add_cls(TreUSE00A)    
    
# One of the common issues with NITF is the need to do special formatting
# for a particular field.
#
# This falls into two categories:
#
# 1. There is a formatting for a field that pynitf isn't doing correctly
#    (e.g., what amounts to a bug in pynitf)
# 2. A particular formatting that is needed by a partner that we are
#    sending files to. In some cases this can just be a tool that has
#    a more restrictive formatting assumption than the standard (e.g.,
#    it *requires* a '+' before a positive number even if the NITF standard
#    documentation doesn't), or it requires a format that is actually
#    wrong (e.g., what amounts to a bug in the tool they are using, but where
#    the tool isn't going to be updated and we need to conform to the wrong
#    format).
#
# One of the advantages of python is that it is a dynamic language. All the
# NITF handling can be changed at run time.
#
# Note that often you need to modify the writing of a NITF field, but not
# do anything special for the reading. Many of our field handlers just use
# the normal python command (e.g., 'float' to get a float), which doesn't
# assume much about the format. So if we modify a field to a "+10.0" or a
# " 10.0" or a "10.0" all get parsed without change.
#
# However in some cases you do need to update the reading also.
#
# In the case of (1), this should ultimately get fixed in pynitf - a
# bug report should be submitted and pynitf changed. But even in that case
# it can useful to dynamically fix this in a particular program until a
# new version of pynitf is available. So a useful procedure is to fix it
# first in your application, report the problem to pynitf, and then when
# you update to new version of pynitf remove your local fix.

def test_no_change(isolated_dir):
    '''This just creates a simple file with one image segment and
    adds a USE00A TRE. We use this TRE just because it is simple and
    a nice one for testing.'''
    f = NitfFile()
    create_image_seg(f)
    create_tre(f.image_segment[0])
    tre = f.image_segment[0].tre_list[0]
    tre.obl_ang = 1.0
    f.write("test.ntf")
    f2 = NitfFile("test.ntf")
    tre2 = f2.image_segment[0].tre_list[0]
    # Float value is as expected
    assert tre2.obl_ang == 1.0
    # Raw bytes have 0 leading fill, with exactly 2 digits after decimal point
    assert tre2.get_raw_bytes("obl_ang") == b"01.00"

# Our partner Yoyodyne insists
# that we supply this number with leading spaces (instead of 0), and with only
# 1 digit after the decimal place.

# The easiest way to do this as a one off (e.g., something quick and dirty for
# test data) is to pass a 'NitfLiteral'. This is a special class in pynitf
# used to say "use this exact string". The string is padded to be the right
# size for the NITF file (using python ljust to add trailing spaces), but is
# otherwise unchanged.

def test_nitf_literal(isolated_dir):
    f = NitfFile()
    create_image_seg(f)
    create_tre(f.image_segment[0])
    tre = f.image_segment[0].tre_list[0]
    tre.obl_ang = NitfLiteral(b"  1.0")
    f.write("test.ntf")
    f2 = NitfFile("test.ntf")
    tre2 = f2.image_segment[0].tre_list[0]
    # Float value is as expected
    assert tre2.obl_ang == 1.0
    # Raw bytes have 0 leading fill, with exactly 2 digits after decimal point
    assert tre2.get_raw_bytes("obl_ang") == b"  1.0"

# After supplying the test file to Yoyodyne, we determine that we want to
# be able to produce a number of files with this new format. We want to
# modify the TRE in our local application to use the new format for all files.
#
# Note this is also very similar to the use case of having a bug fix against
# pynitf (e.g. Yoyodyne's format matches the standard and pynitf doesn't).
# We may need to handle things locally until pynitf is updated, or perhaps
# we have a set of changes we want to work out/batch together before modifying
# pynitf.
#
# The way to do this is to modify how pynitf handles the TRE. All the
# TREs are handled by classes registered in tre_tag_to_cls (a
# instance of TreTagToCls). You can either create an entirely new TRE class,
# or just copy and modify the existing class.
    
def test_tre_modify(isolated_dir, modify_use00a_tre):
    # Most of the TREs are instances of the Tre class, which is
    # in turn and instance of FieldStruct that has the class specified
    # as a "desc" table. This *isn't* required, you just need to supply
    # the same functions as Tre has, or you can supply a
    # tre_implementation_class. But for this example we make a class
    # derived from the Tre.

    # Since we are only changing one field, we start with the existing
    # TreUSE00A desc table. An alternative is just to create an entirely
    # new table
    my_desc = copy.deepcopy(TreUSE00A.desc)
    ind = [i for i,d in enumerate(my_desc) if d[0] == "obl_ang"][0]
    my_desc[ind] = ["obl_ang", "Obliquity Angle", 5, float,
                    # frmt was "%05.2lf" for 2 digits after decimal point,
                    # 0 filled on left. Change to 1 digit, space filled.
                    {"frmt" : "%5.1lf", "optional" :True}]
    class MyTreUSE00A(Tre):
        __doc__ = TreUSE00A.__doc__
        desc = my_desc
        tre_tag = TreUSE00A.tre_tag
    tre_tag_to_cls.add_cls(MyTreUSE00A)

    # Now test on a new file
    f = NitfFile()
    create_image_seg(f)
    t = MyTreUSE00A()
    t.angle_to_north = 270
    t.mean_gsd = 105.2
    t.dynamic_range = 2047
    t.obl_ang = 1.0
    t.roll_ang = -21.15
    t.n_ref = 0
    t.rev_num = 3317
    t.n_seg = 1
    t.max_lp_seg = 6287
    t.sun_el = 68.5
    t.sun_az = 131.3
    f.image_segment[0].tre_list.append(t)
    f.write("test.ntf")
    f2 = NitfFile("test.ntf")
    tre2 = f2.image_segment[0].tre_list[0]
    # Float value is as expected
    assert tre2.obl_ang == 1.0
    # Raw bytes have space leading fill, with exactly 1 digit after
    # decimal point
    assert tre2.get_raw_bytes("obl_ang") == b"  1.0"

# Sometimes a format is complicated enough it can't be captured with with
# a format string.
# For example Yoyodyne *must* have the float with 2 digits after the decimal
# point zero filled, unless it is > 20 in which case it needs to use 1 digit
# space filled.
#
# Basic structure of this test is like the last one, except we supply a
# formatting function instead of a format string

def test_tre_modify_complicated_format(isolated_dir, modify_use00a_tre):
    def my_format(v):
        if(v > 20):
            return "%5.1lf" % v
        return "%05.2lf" %v
    
    my_desc = copy.deepcopy(TreUSE00A.desc)
    ind = [i for i,d in enumerate(my_desc) if d[0] == "obl_ang"][0]
    my_desc[ind] = ["obl_ang", "Obliquity Angle", 5, float,
                    {"frmt" : my_format, "optional" :True}]
    class MyTreUSE00A(Tre):
        __doc__ = TreUSE00A.__doc__
        desc = my_desc
        tre_tag = TreUSE00A.tre_tag
    tre_tag_to_cls.add_cls(MyTreUSE00A)

    # Now test on a new file
    f = NitfFile()
    create_image_seg(f)
    create_image_seg(f)
    t = MyTreUSE00A()
    t.angle_to_north = 270
    t.mean_gsd = 105.2
    t.dynamic_range = 2047
    t.obl_ang = 1.0
    t.roll_ang = -21.15
    t.n_ref = 0
    t.rev_num = 3317
    t.n_seg = 1
    t.max_lp_seg = 6287
    t.sun_el = 68.5
    t.sun_az = 131.3
    f.image_segment[0].tre_list.append(t)
    t = MyTreUSE00A()
    t.angle_to_north = 270
    t.mean_gsd = 105.2
    t.dynamic_range = 2047
    t.obl_ang = 30.0
    t.roll_ang = -21.15
    t.n_ref = 0
    t.rev_num = 3317
    t.n_seg = 1
    t.max_lp_seg = 6287
    t.sun_el = 68.5
    t.sun_az = 131.3
    f.image_segment[1].tre_list.append(t)
    f.write("test.ntf")
    f2 = NitfFile("test.ntf")
    tre2 = f2.image_segment[0].tre_list[0]
    tre3 = f2.image_segment[1].tre_list[0]
    # Float value is as expected
    assert tre2.obl_ang == 1.0
    assert tre3.obl_ang == 30.0
    # Raw bytes have 0 leading fill, with exactly 2 digit after
    # decimal point
    assert tre2.get_raw_bytes("obl_ang") == b"01.00"
    # Raw bytes have space leading fill, with exactly 1 digit after
    # decimal point
    assert tre3.get_raw_bytes("obl_ang") == b" 30.0"
    

# Even more complicated, there can be formats that can't use the
# normal format string for either reading and writing.
#
# For example Yoyodyne has decided that what it really needs is the
# number to zero filled, using a space, and written backwards.
#
# The most general formatting takes a class that is derived from
# pynitf.FieldData (or alternatively, just provides the same interface if
# deriving from it is inconvenient).

def test_tre_modify_even_more_complicated_format(isolated_dir,
                                                 modify_use00a_tre):
    class ReverseNumber(FieldData):
        def get_print(self, key):
            t = self[key]
            if(t is None or len(t) == 0):
                return "Not used"
            return "%f" % t

        def unpack(self, key, v):
            return float(v.replace(b" ", b".")[::-1])
        
        def pack(self, key, v):
            return (b"%05.2f" % v).replace(b".",b" ")[::-1]

    my_desc = copy.deepcopy(TreUSE00A.desc)
    ind = [i for i,d in enumerate(my_desc) if d[0] == "obl_ang"][0]
    my_desc[ind] = ["obl_ang", "Obliquity Angle", 5, float,
                    {"field_value_class" : ReverseNumber, "optional" :True,
                     "size_not_updated" : True }]
    class MyTreUSE00A(Tre):
        __doc__ = TreUSE00A.__doc__
        desc = my_desc
        tre_tag = TreUSE00A.tre_tag
    tre_tag_to_cls.add_cls(MyTreUSE00A)

    # Now test on a new file
    f = NitfFile()
    create_image_seg(f)
    t = MyTreUSE00A()
    t.angle_to_north = 270
    t.mean_gsd = 105.2
    t.dynamic_range = 2047
    t.obl_ang = 1.0
    t.roll_ang = -21.15
    t.n_ref = 0
    t.rev_num = 3317
    t.n_seg = 1
    t.max_lp_seg = 6287
    t.sun_el = 68.5
    t.sun_az = 131.3
    f.image_segment[0].tre_list.append(t)
    f.write("test.ntf")
    f2 = NitfFile("test.ntf")
    tre2 = f2.image_segment[0].tre_list[0]
    # Float value is as expected
    assert tre2.obl_ang == 1.0
    # Raw bytes have 0 leading fill, with exactly 2 digit after
    # decimal point, decimal point is a space, and in reverse order
    assert tre2.get_raw_bytes("obl_ang") == b"00 10"
    
            
