from pynitf.nitf_field import *
from pynitf.nitf_file_diff import NitfDiff
from pynitf.nitf_diff_handle import AlwaysTrueHandle, NitfDiffHandle
from pynitf_test_support import *
import io
import math
from pynitf_test_support import *
import copy
import logging
import struct

@pytest.yield_fixture(scope="function")
def nitf_diff_field_struct(print_logging):
    '''Set up a NitfDiff object that just compares field structure 
    objects'''
    d = NitfDiff()
    d.handle_set.clear()
    d.handle_set.add_handle(FieldStructDiff(), priority_order = 1)
    d.handle_set.add_handle(AlwaysTrueHandle(), priority_order = 0)
    with d.diff_context("Field Structure"):
        yield d

def test_float_to_fixed_width():
    assert len(float_to_fixed_width(evil_float1, 7)) <= 7
    assert len(float_to_fixed_width(evil_float2, 7)) <= 7
    assert len(float_to_fixed_width(evil_float3, 7, maximum_precision=True)) <= 7
    if(False):
        for i in range(-7,7):
            print(float_to_fixed_width(pow(10,i), 7))

            
def test_nitf_field_basic_str():
    '''Basic str type test for NitfField'''
    f = NitfField(None, "foo", 4, str, None, {})
    f[()] = "blah"
    assert f[()] == "blah"
    assert f.bytes() == b"blah"
    fh = io.BytesIO()
    f.write_to_file(fh, ())
    assert fh.getvalue() == b"blah"
    f[()] = "fred"
    assert fh.getvalue() == b"blah"
    f.update_file(fh, ())
    assert fh.getvalue() == b"fred"
    f2 = NitfField(None, "foo", 4, str, None, {})
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2,False,())
    assert f2[()] == "fred"

def test_nitf_field_basic_int():
    '''Basic int type test for NitfField'''
    f = NitfField(None, "foo", 4, int, None, {})
    f[()] = 1
    assert f[()] == 1
    assert f.bytes() == b"0001"
    fh = io.BytesIO()
    f.write_to_file(fh,())
    assert fh.getvalue() == b"0001"
    f2 = NitfField(None, "foo", 4, int, None, {})
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2,False,())
    assert f2[()] == 1
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2, True,())
    assert f2[()] == 1
    assert f2.get_raw_bytes(()) == b"0001"

def test_nitf_field_basic_float():
    '''Basic float type test for NitfField'''
    f = NitfField(None, "foo", 8, float, None, {})
    f[()] = 1.23
    assert f[()] == 1.23
    assert f.bytes() == b"1.230000"
    fh = io.BytesIO()
    f.write_to_file(fh,())
    assert fh.getvalue() == b"1.230000"
    f2 = NitfField(None, "foo", 8, float, None, {})
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2,False,())
    assert f2[()] == 1.23
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2, True,())
    assert f2[()] == 1.23
    assert f2.get_raw_bytes(()) == b"1.230000"

def test_nitf_field_frmt():
    '''Test NitfField with frmt string'''
    f = NitfField(None, "foo", 8, float, None, {"frmt" : "%07.2lf"})
    f[()] = 1.23
    assert f[()] == 1.23
    assert f.bytes() == b"0001.23 "
    fh = io.BytesIO()
    f.write_to_file(fh,())
    assert fh.getvalue() == b"0001.23 "
    f2 = NitfField(None, "foo", 8, float, None, {})
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2,False,())
    assert f2[()] == 1.23
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2, True,())
    assert f2[()] == 1.23
    assert f2.get_raw_bytes(()) == b"0001.23 "

def test_nitf_field_frmt():
    '''Test NitfField with frmt function'''
    # This is taken from the RPC code
    def _tre_rpc_coeff_format(v):
        t = "%+010.6lE" % v
        # Replace 2 digit exponent with 1 digit
        t = re.sub(r'E([+-])0', r'E\1', t)
        return t
    
    f = NitfField(None, "foo", 12, float, None,
                  {"frmt" : _tre_rpc_coeff_format})
    f[()] = 1.23
    assert f[()] == 1.23
    assert f.bytes() == b"+1.230000E+0"
    fh = io.BytesIO()
    f.write_to_file(fh,())
    assert fh.getvalue() == b"+1.230000E+0"
    f2 = NitfField(None, "foo", 12, float, None, {})
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2,False,())
    assert f2[()] == 1.23
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2, True, ())
    assert f2[()] == 1.23
    assert f2.get_raw_bytes(()) == b"+1.230000E+0"

def test_nitf_field_default():
    '''Test NitfField with default value'''
    f = NitfField(None, "foo", 4, int, None, {"default" : 20})
    assert f[()] == 20
    assert f.bytes() == b"0020"
    f[()] = 10
    assert f[()] == 10

def test_nitf_field_hardcoded_value():
    '''Test NitfField with hardcoded_value'''
    f = NitfField(None, "foo", 4, int, None,
                  {"default" : 20, "hardcoded_value" : True})
    assert f[()] == 20
    assert f.bytes() == b"0020"
    with pytest.raises(RuntimeError):
        f[()] = 10

def test_nitf_field_optional():
    '''Test NitfField with optional'''
    f = NitfField(None, "foo", 4, int, None, {})
    with pytest.raises(RuntimeError):
        f[()] = None
    f = NitfField(None, "foo", 4, int, None, {"optional" : True})
    f[()] = None
    assert f[()] == None
    assert f.bytes() == b"    "
    fh = io.BytesIO()
    f.write_to_file(fh,())
    assert fh.getvalue() == b"    "
    f2 = NitfField(None, "foo", 4, int, None, {"optional" : True})
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2,False,())
    assert f2[()] == None
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2, True, ())
    assert f2[()] == None
    assert f2.get_raw_bytes(()) == b"    "

def test_nitf_field_optional_char():
    '''Test NitfField with optional_char'''
    f = NitfField(None, "foo", 4, int, None, {})
    with pytest.raises(RuntimeError):
        f[()] = None
    f = NitfField(None, "foo", 4, int, None, {"optional" : True,
                                              "optional_char" : '-'})
    f[()] = None
    assert f[()] == None
    assert f.bytes() == b"----"
    fh = io.BytesIO()
    f.write_to_file(fh,())
    assert fh.getvalue() == b"----"
    f2 = NitfField(None, "foo", 4, int, None, {"optional" : True,
                                               "optional_char" : '-'})
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2,False,())
    assert f2[()] == None
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2, True, ())
    assert f2[()] == None
    assert f2.get_raw_bytes(()) == b"----"

def test_string_field_data():
    f = StringFieldData(None, "foo", 12, None, None,
                           {"field_value_class" : StringFieldData,
                            "size_not_updated" : True})
    f[()] = "blahblahblah"
    assert f[()] == "blahblahblah"
    assert f.bytes() == b"blahblahblah"

def test_float_field_data():
    f = FloatFieldData(None, "foo", 4, None, None,
                          {"field_value_class" : FloatFieldData,
                           "size_not_updated" : True})
    f[()] = 1.23
    assert f[()] == pytest.approx(1.23)
    assert struct.unpack(">f", f.bytes())[0] == pytest.approx(1.23)
    fh = io.BytesIO()
    f.write_to_file(fh,())
    f2 = FloatFieldData(None, "foo", 4, None, None,
                          {"field_value_class" : FloatFieldData,
                           "size_not_updated" : True})
    fh2 = io.BytesIO(fh.getvalue())
    f2.read_from_file(fh2,False,())
    assert f2[()] == pytest.approx(1.23)

def test_int_field_data():
    for sgn in (True, False):
        for sz in (1, 2, 3, 4, 8):
            f = IntFieldData(None, "foo", sz, None, None,
                                {"field_value_class" : IntFieldData,
                                 "size_not_updated" : True,
                                 "signed" : sgn})
            f[()] = 123
            assert f[()] == 123
            fh = io.BytesIO()
            f.write_to_file(fh,())
            f2 = IntFieldData(None, "foo", sz, None, None,
                                 {"field_value_class" : IntFieldData,
                                  "size_not_updated" : True,
                                  "signed" : sgn})
            fh2 = io.BytesIO(fh.getvalue())
            f2.read_from_file(fh2,False,())
            assert f2[()] == 123
            

# TODO Rework NitfField, should be able to handle the lambda for the
# defaultdict so we can use pickle. Unfortunately multiprocessing doesn't
# work out of the box with dill, so it would be desirable to have plain
# pickling working
@skip(reason="don't want to assume dill is available")
def test_field_struct_dill():
    '''Simple field struct, see that we can set and read values.'''
    # We use lambdas, so pickle doesn't work. But should be able to
    # use dill
    import dill
    desc = [["fhdr", "", 4, str,  {"default" : "NITF"}],
            ["clevel", "", 2, int ],]
    t = FieldStruct(desc)
    p = dill.dumps(t)
    t2 = dill.loads(p)
    
def test_field_struct_conditional():
    class TestFieldStruct(FieldStruct):
        desc = [["fhdr", "", 4, str, {"default" : "NITF"}],
                ["udhdl", "", 5, int],
                ["udhofl", "", 3, int, {"condition" : "f.udhdl != 0"}],
                ["flttst", "", 10, float, {"condition" : "f.udhdl != 0"}],
               ]
    t = TestFieldStruct()
    with pytest.raises(RuntimeError):
        t.udhofl = 1
    fh = io.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF00000'
    assert t.udhofl is None
    assert t.flttst is None
    assert list(t.items()) == [('fhdr', 'NITF'), ('udhdl', 0), ('udhofl', None),
                               ('flttst', None)]
    t.udhdl = 10
    t.udhofl = 20
    t.flttst = 1.123467
    fh = io.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF000100201.12346700'
    assert t.udhofl == 20
    assert list(t.items()) == [('fhdr', 'NITF'), ('udhdl', 10), ('udhofl', 20),
                               ('flttst', 1.123467)]
        
def test_field_struct_basic(nitf_diff_field_struct):
    '''Basic test, just set and read values.'''
    d = nitf_diff_field_struct # Shorter name
    class TestFieldStruct(FieldStruct):
        desc = [["fhdr", "", 4, str,  {"default" : "NITF"}],
                ["clevel", "", 2, int ],]
    t = TestFieldStruct()
    assert t.fhdr == "NITF"
    t.fhdr = 'FOO'
    assert t.fhdr == "FOO"
    t.clevel = 1
    assert list(t.items()) == [('fhdr', 'FOO'), ('clevel', 1)]
    fh = io.BytesIO()
    t.write_to_file(fh)
    assert d.compare_obj(t, t) == True
    assert fh.getvalue() == b'FOO 01'
    fh2 = io.BytesIO(b'BOO 02')
    t2 = TestFieldStruct()
    t2.read_from_file(fh2)
    assert t2.fhdr == "BOO"
    assert t2.clevel == 2
    assert str(t2) == \
'''fhdr  : BOO
clevel: 2
'''
    assert d.compare_obj(t, t2) == False
    t2 = TestFieldStruct()
    t2.fhdr = 'FOO'
    t2.clevel2 = 1
    assert d.compare_obj(t, t2) == False


def test_loop(nitf_diff_field_struct):
    '''Test where we have a looping structure'''
    d = nitf_diff_field_struct # Shorter name
    class TestFieldStruct(FieldStruct):
        desc = [["fhdr", "", 4, str, {"default" : "NITF"}],
                ["numi", "", 3, int],
                [["loop", "f.numi"],
                 ['lish', "", 6, int],
                 ['li', "", 10, int]]
        ]
    t = TestFieldStruct()
    t.numi = 4
    t.lish[0] = 1
    t.lish[1] = 2
    t.lish[2] = 3
    t.lish[3] = 4
    t.li[0] = 5
    t.li[1] = 6
    t.li[2] = 7
    t.li[3] = 8
    with pytest.raises(IndexError):
        t.li[4] = 9
    with pytest.raises(IndexError):
        t.li[-1] = 9
    with pytest.raises(RuntimeError):
        t.li[1:3] = 9
    assert list(t.lish) == [1,2,3,4]
    assert list(t.li) == [5,6,7,8]
    assert str(t) == \
'''fhdr: NITF
numi: 4
Loop - f.numi
  lish[0]: 1
  lish[1]: 2
  lish[2]: 3
  lish[3]: 4
  li[0]  : 5
  li[1]  : 6
  li[2]  : 7
  li[3]  : 8
'''
    assert list(t.items()) == [('fhdr', 'NITF'), ('numi', 4), ('lish', [1, 2, 3, 4]), ('li', [5, 6, 7, 8])]
    fh = io.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF0040000010000000005000002000000000600000300000000070000040000000008'
    t2 = copy.deepcopy(t)
    assert d.compare_obj(t, t2) == True
    t2.li[1] = 17
    assert d.compare_obj(t, t2) == False
    

def test_nested_loop(nitf_diff_field_struct):
    d = nitf_diff_field_struct # Shorter name
    class TestFieldStruct(FieldStruct):
        desc = [["fhdr", "", 4, str, {"default" : "NITF"}],
                ["numi", "", 3, int],
                [["loop", "f.numi"],
                 ['lish', "", 6, int],
                 ["numj", "", 3, int],
                 [["loop", "f.numj[i1]"],
                  ['li', "", 10, int]]
                ]]
    t = TestFieldStruct()
    t.numi = 2
    t.numj[0] = 3
    t.numj[1] = 4
    t.li[0,1] = 10
    t.li[1,3] = 20
    assert t.li[0,1] == 10
    assert t.li[1,3] == 20
    with pytest.raises(IndexError):
        t.li[1,4]
    with pytest.raises(IndexError):
        t.li[2,1]
    assert list(t.items()) == [('fhdr', 'NITF'), ('numi', 2), ('lish', [0, 0]), ('numj', [3, 4]), ('li', [[0, 10, 0], [0, 0, 0, 20]])]
    fh = io.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF0020000000030000000000000000001000000000000000000040000000000000000000000000000000000000020' 
    fh2 = io.BytesIO(fh.getvalue())
    t2 = TestFieldStruct()
    t2.read_from_file(fh2)
    assert str(t) == str(t2)
    assert d.compare_obj(t, t2) == True
    t2.li[1,3] = 17
    assert d.compare_obj(t, t2) == False
    assert str(t) == '''fhdr: NITF
numi: 2
Loop - f.numi
  lish[0]: 0
  lish[1]: 0
  numj[0]: 3
  numj[1]: 4
  Loop - f.numj[i1]
    li[0, 0]: 0
    li[0, 1]: 10
    li[0, 2]: 0
    li[1, 0]: 0
    li[1, 1]: 0
    li[1, 2]: 0
    li[1, 3]: 20
'''

def test_nested_loop2(nitf_diff_field_struct):
    d = nitf_diff_field_struct # Shorter name
    # The "mark1" through "mark3" make it easier to look at the write out
    # of the TRE and make sure things are going into the correct spot, and
    # that we are reading this correctly.
    class TestFieldStruct(FieldStruct):
        desc = [["fhdr", "", 4, str, {"default" : "NITF"}],
                ["numi", "", 3, int],
                [["loop", "f.numi"],
                 ["mark1", "", 5, str, {"default":"mark1"}],
                 ['lish', "", 6, int],
                 ["numj", "", 3, int],
                 [["loop", "f.numj[i1]"],
                  ["mark2", "", 5,str, {"default":"mark2"}],
                  ["numk", "", 3, int],
                  [["loop", "f.numk[i1,i2]"],
                   ["mark3", "", 5, str, {"default":"mark3"}],
                   ['li', "", 10, int],
                  ],
                 ],
                ],            
        ]
    t = TestFieldStruct()
    t.numi = 2
    t.numj[0] = 2
    t.numj[1] = 4
    t.numk[0,0] = 3
    t.numk[0,1] = 3
    t.numk[1,0] = 4
    t.numk[1,1] = 4
    t.numk[1,2] = 4
    t.numk[1,3] = 4
    t.li[0,1,1] = 10
    t.li[1,3,1] = 20
    assert t.li[0,1,1] == 10
    assert t.li[1,3,1] == 20
    with pytest.raises(IndexError):
        t.li[0,4,0]
    with pytest.raises(IndexError):
        t.li[2,1,1]
    val = 10
    for i1 in range(t.numi):
        for i2 in range(t.numj[i1]):
            for i3 in range(t.numk[i1,i2]):
                t.li[i1,i2,i3] = val
                val += 1
    val = 10
    for i1 in range(t.numi):
        for i2 in range(t.numj[i1]):
            for i3 in range(t.numk[i1,i2]):
                assert t.li[i1,i2,i3] == val
                val += 1
    fh = io.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF002mark1000000002mark2003mark30000000010mark30000000011mark30000000012mark2003mark30000000013mark30000000014mark30000000015mark1000000004mark2004mark30000000016mark30000000017mark30000000018mark30000000019mark2004mark30000000020mark30000000021mark30000000022mark30000000023mark2004mark30000000024mark30000000025mark30000000026mark30000000027mark2004mark30000000028mark30000000029mark30000000030mark30000000031'
    fh2 = io.BytesIO(fh.getvalue())
    t2 = TestFieldStruct()
    t2.read_from_file(fh2)
    fh2 = io.BytesIO()
    t2.write_to_file(fh2)
    val = 10
    for i1 in range(t.numi):
        for i2 in range(t.numj[i1]):
            for i3 in range(t.numk[i1,i2]):
                assert t2.li[i1,i2,i3] == val
                val += 1
    assert str(t) == str(t2)
    assert d.compare_obj(t, t2) == True
    t2.li[1,3,1] = 17
    assert d.compare_obj(t, t2) == False
    if False:
        print("-----------------------------------------------")
        print(t)
        print("-----------------------------------------------")
        
    assert str(t) == '''fhdr: NITF
numi: 2
Loop - f.numi
  mark1[0]: mark1
  mark1[1]: mark1
  lish[0] : 0
  lish[1] : 0
  numj[0] : 2
  numj[1] : 4
  Loop - f.numj[i1]
    mark2[0, 0]: mark2
    mark2[0, 1]: mark2
    mark2[1, 0]: mark2
    mark2[1, 1]: mark2
    mark2[1, 2]: mark2
    mark2[1, 3]: mark2
    numk[0, 0] : 3
    numk[0, 1] : 3
    numk[1, 0] : 4
    numk[1, 1] : 4
    numk[1, 2] : 4
    numk[1, 3] : 4
    Loop - f.numk[i1,i2]
      mark3[0, 0, 0]: mark3
      mark3[0, 0, 1]: mark3
      mark3[0, 0, 2]: mark3
      mark3[0, 1, 0]: mark3
      mark3[0, 1, 1]: mark3
      mark3[0, 1, 2]: mark3
      mark3[1, 0, 0]: mark3
      mark3[1, 0, 1]: mark3
      mark3[1, 0, 2]: mark3
      mark3[1, 0, 3]: mark3
      mark3[1, 1, 0]: mark3
      mark3[1, 1, 1]: mark3
      mark3[1, 1, 2]: mark3
      mark3[1, 1, 3]: mark3
      mark3[1, 2, 0]: mark3
      mark3[1, 2, 1]: mark3
      mark3[1, 2, 2]: mark3
      mark3[1, 2, 3]: mark3
      mark3[1, 3, 0]: mark3
      mark3[1, 3, 1]: mark3
      mark3[1, 3, 2]: mark3
      mark3[1, 3, 3]: mark3
      li[0, 0, 0]   : 10
      li[0, 0, 1]   : 11
      li[0, 0, 2]   : 12
      li[0, 1, 0]   : 13
      li[0, 1, 1]   : 14
      li[0, 1, 2]   : 15
      li[1, 0, 0]   : 16
      li[1, 0, 1]   : 17
      li[1, 0, 2]   : 18
      li[1, 0, 3]   : 19
      li[1, 1, 0]   : 20
      li[1, 1, 1]   : 21
      li[1, 1, 2]   : 22
      li[1, 1, 3]   : 23
      li[1, 2, 0]   : 24
      li[1, 2, 1]   : 25
      li[1, 2, 2]   : 26
      li[1, 2, 3]   : 27
      li[1, 3, 0]   : 28
      li[1, 3, 1]   : 29
      li[1, 3, 2]   : 30
      li[1, 3, 3]   : 31
'''
    
def test_nested_loop3(nitf_diff_field_struct):
    d = nitf_diff_field_struct # Shorter name
    # The "mark1" through "mark3" make it easier to look at the write out
    # of the TRE and make sure things are going into the correct spot, and
    # that we are reading this correctly.
    class TestFieldStruct(FieldStruct):
        desc = [["fhdr", "", 4, str, {"default" : "NITF"}],
                ["numi", "", 3, int],
                [["loop", "f.numi"],
                 ["mark1", "", 5, str, {"default":"mark1"}],
                 ["numj", "", 3, int],
                 [["loop", "f.numj[i1]"],
                  ["mark2", "", 5,str, {"default":"mark2"}],
                  ["numk", "", 3, int],
                  [["loop", "f.numk[i1,i2]"],
                   ["mark3", "", 5, str, {"default":"mark3"}],
                   ["numl", "", 3, int],
                   [["loop", "f.numl[i1,i2,i3]"],
                    ['li', "", 10, int],
                   ]
                  ],
                 ],
                ],]
    t = TestFieldStruct()
    t.numi = 2
    t.numj[0] = 2
    t.numj[1] = 4
    t.numk[0,0] = 2
    t.numk[0,1] = 2
    t.numk[1,0] = 2
    t.numk[1,1] = 2
    t.numk[1,2] = 2
    t.numk[1,3] = 2
    t.numl[0,0,0]=3
    t.numl[0,0,1]=3
    t.numl[0,1,0]=3
    t.numl[0,1,1]=3
    t.numl[1,0,0]=3
    t.numl[1,0,1]=3
    t.numl[1,1,0]=3
    t.numl[1,1,1]=3
    t.numl[1,2,0]=3
    t.numl[1,2,1]=3
    t.numl[1,3,0]=3
    t.numl[1,3,1]=3
    t.li[0,1,1,1] = 10
    t.li[1,3,1,0] = 20
    assert t.li[0,1,1,1] == 10
    assert t.li[1,3,1,0] == 20
    val = 10
    for i1 in range(t.numi):
        for i2 in range(t.numj[i1]):
            for i3 in range(t.numk[i1,i2]):
                for i4 in range(t.numl[i1,i2,i3]):
                    t.li[i1,i2,i3,i4] = val
                    val += 1
    val = 10
    for i1 in range(t.numi):
        for i2 in range(t.numj[i1]):
            for i3 in range(t.numk[i1,i2]):
                for i4 in range(t.numl[i1,i2, i3]):
                    assert t.li[i1,i2,i3,i4] == val
                    val += 1
    assert list(t.items()) == [('fhdr', 'NITF'), ('numi', 2), ('mark1', ['mark1', 'mark1']), ('numj', [2, 4]), ('mark2', [['mark2', 'mark2'], ['mark2', 'mark2', 'mark2', 'mark2']]), ('numk', [[2, 2], [2, 2, 2, 2]]), ('mark3', [[['mark3', 'mark3'], ['mark3', 'mark3']], [['mark3', 'mark3'], ['mark3', 'mark3'], ['mark3', 'mark3'], ['mark3', 'mark3']]]), ('numl', [[[3, 3], [3, 3]], [[3, 3], [3, 3], [3, 3], [3, 3]]]), ('li', [[[[10, 11, 12], [13, 14, 15]], [[16, 17, 18], [19, 20, 21]]], [[[22, 23, 24], [25, 26, 27]], [[28, 29, 30], [31, 32, 33]], [[34, 35, 36], [37, 38, 39]], [[40, 41, 42], [43, 44, 45]]]])]
    fh = io.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF002mark1002mark2002mark3003000000001000000000110000000012mark3003000000001300000000140000000015mark2002mark3003000000001600000000170000000018mark3003000000001900000000200000000021mark1004mark2002mark3003000000002200000000230000000024mark3003000000002500000000260000000027mark2002mark3003000000002800000000290000000030mark3003000000003100000000320000000033mark2002mark3003000000003400000000350000000036mark3003000000003700000000380000000039mark2002mark3003000000004000000000410000000042mark3003000000004300000000440000000045'
    fh2 = io.BytesIO(fh.getvalue())
    t2 = TestFieldStruct()
    t2.read_from_file(fh2)
    fh2 = io.BytesIO()
    t2.write_to_file(fh2)
    val = 10
    expected_items = []
    for i1 in range(t2.numi):
        for i2 in range(t2.numj[i1]):
            for i3 in range(t2.numk[i1,i2]):
                for i4 in range(t2.numl[i1,i2, i3]):
                    assert t2.li[i1,i2,i3,i4] == val
                    expected_items.append(((i1,i2,i3,i4), val))
                    val += 1
    assert str(t) == str(t2)
    assert NitfField.is_shape_equal(t.li, t2.li)
    assert list(t.li.values()) == list([itm[1] for itm in expected_items])
    assert list(t.li.items()) == expected_items
    assert d.compare_obj(t, t2) == True
    t2.li[1,3,1,0] = 17
    assert d.compare_obj(t, t2) == False
    t2.numl[1,3,1]=t.numl[1,3,1]+1
    assert not NitfField.is_shape_equal(t.li, t2.li)
    assert d.compare_obj(t, t2) == False
    assert str(t) == '''fhdr: NITF
numi: 2
Loop - f.numi
  mark1[0]: mark1
  mark1[1]: mark1
  numj[0] : 2
  numj[1] : 4
  Loop - f.numj[i1]
    mark2[0, 0]: mark2
    mark2[0, 1]: mark2
    mark2[1, 0]: mark2
    mark2[1, 1]: mark2
    mark2[1, 2]: mark2
    mark2[1, 3]: mark2
    numk[0, 0] : 2
    numk[0, 1] : 2
    numk[1, 0] : 2
    numk[1, 1] : 2
    numk[1, 2] : 2
    numk[1, 3] : 2
    Loop - f.numk[i1,i2]
      mark3[0, 0, 0]: mark3
      mark3[0, 0, 1]: mark3
      mark3[0, 1, 0]: mark3
      mark3[0, 1, 1]: mark3
      mark3[1, 0, 0]: mark3
      mark3[1, 0, 1]: mark3
      mark3[1, 1, 0]: mark3
      mark3[1, 1, 1]: mark3
      mark3[1, 2, 0]: mark3
      mark3[1, 2, 1]: mark3
      mark3[1, 3, 0]: mark3
      mark3[1, 3, 1]: mark3
      numl[0, 0, 0] : 3
      numl[0, 0, 1] : 3
      numl[0, 1, 0] : 3
      numl[0, 1, 1] : 3
      numl[1, 0, 0] : 3
      numl[1, 0, 1] : 3
      numl[1, 1, 0] : 3
      numl[1, 1, 1] : 3
      numl[1, 2, 0] : 3
      numl[1, 2, 1] : 3
      numl[1, 3, 0] : 3
      numl[1, 3, 1] : 3
      Loop - f.numl[i1,i2,i3]
        li[0, 0, 0, 0]: 10
        li[0, 0, 0, 1]: 11
        li[0, 0, 0, 2]: 12
        li[0, 0, 1, 0]: 13
        li[0, 0, 1, 1]: 14
        li[0, 0, 1, 2]: 15
        li[0, 1, 0, 0]: 16
        li[0, 1, 0, 1]: 17
        li[0, 1, 0, 2]: 18
        li[0, 1, 1, 0]: 19
        li[0, 1, 1, 1]: 20
        li[0, 1, 1, 2]: 21
        li[1, 0, 0, 0]: 22
        li[1, 0, 0, 1]: 23
        li[1, 0, 0, 2]: 24
        li[1, 0, 1, 0]: 25
        li[1, 0, 1, 1]: 26
        li[1, 0, 1, 2]: 27
        li[1, 1, 0, 0]: 28
        li[1, 1, 0, 1]: 29
        li[1, 1, 0, 2]: 30
        li[1, 1, 1, 0]: 31
        li[1, 1, 1, 1]: 32
        li[1, 1, 1, 2]: 33
        li[1, 2, 0, 0]: 34
        li[1, 2, 0, 1]: 35
        li[1, 2, 0, 2]: 36
        li[1, 2, 1, 0]: 37
        li[1, 2, 1, 1]: 38
        li[1, 2, 1, 2]: 39
        li[1, 3, 0, 0]: 40
        li[1, 3, 0, 1]: 41
        li[1, 3, 0, 2]: 42
        li[1, 3, 1, 0]: 43
        li[1, 3, 1, 1]: 44
        li[1, 3, 1, 2]: 45
'''
    
def test_conditional(nitf_diff_field_struct):
    d = nitf_diff_field_struct # Shorter name
    class TestFieldStruct(FieldStruct):
        desc = [["fhdr", "", 4, str, {"default" : "NITF"}],
                ["udhdl", "", 5, int],
                ["udhofl", "", 3, int, {"condition" : "f.udhdl != 0"}],
                ["flttst", "", 10, float, {"condition" : "f.udhdl != 0"}],]
    t = TestFieldStruct()
    with pytest.raises(RuntimeError):
        t.udhofl = 1
    fh = io.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF00000'
    assert t.udhofl is None
    assert t.flttst is None
    assert list(t.items()) == [('fhdr', 'NITF'), ('udhdl', 0), ('udhofl', None),
                               ('flttst', None)]
    assert d.compare_obj(t, t) == True
    t.udhdl = 10
    t.udhofl = 20
    t.flttst = 1.123467
    assert d.compare_obj(t, t) == True
    fh = io.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF000100201.12346700'
    assert t.udhofl == 20
    assert list(t.items()) == [('fhdr', 'NITF'), ('udhdl', 10), ('udhofl', 20),
                               ('flttst', 1.123467)]
    t2 = copy.deepcopy(t)
    t2.udhofl = 21
    t2.flttst = 1.1234568
    assert d.compare_obj(t, t2) == False
    t2.udhdl = 0
    assert d.compare_obj(t, t2) == False

def test_loop_conditional(nitf_diff_field_struct):
    d = nitf_diff_field_struct # Shorter name
    # udhdl doesn't really loop in a nitf file header, but we'll pretend it
    # does to test a looping conditional
    class TestFieldStruct(FieldStruct):
        desc = [["fhdr", "", 4, str, {"default" : "NITF"}],
                ["numi", "", 3, int],
                [["loop", "f.numi"],
                 ["udhdl", "", 5, int],
                 ["udhofl", "", 3, int, {"condition" : "f.udhdl[i1] != 0"}]]]
    t = TestFieldStruct()
    t.numi = 3
    t.udhdl[1] = 10
    t.udhdl[2] = 20
    assert list(t.udhofl) == [None, 0, 0]
    t.udhofl[1] = 30
    t.udhofl[2] = 40
    assert list(t.udhofl) == [None, 30, 40]
    assert list(t.items()) == [('fhdr', 'NITF'), ('numi', 3), ('udhdl', [0, 10, 20]), ('udhofl', [None, 30, 40])]
    fh = io.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF003000000001003000020040'
    t2 = copy.deepcopy(t)
    assert d.compare_obj(t, t2) == True
    t2.udhofl[2] = 50
    assert d.compare_obj(t, t2) == False
    
# TODO Add a test like Walt had where we override the equality function
# for a field to match ignoring case
