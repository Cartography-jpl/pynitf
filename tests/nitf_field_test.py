from pynitf.nitf_field import *
from pynitf.nitf_file_diff import NitfDiff
from pynitf.nitf_diff_handle import AlwaysTrueHandle, NitfDiffHandle
from pynitf_test_support import *
import io
import math
from pynitf_test_support import *
import copy
import logging

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
        
def test_basic(nitf_diff_field_struct):
    '''Basic test, just set and read values.'''
    d = nitf_diff_field_struct # Shorter name
    TestField = create_nitf_field_structure("TestField",
        [["fhdr", "", 4, str,  {"default" : "NITF"}],
         ["clevel", "", 2, int ],
        ])
    t = TestField()
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
    t2 = TestField()
    t2.read_from_file(fh2)
    assert t2.fhdr == "BOO"
    assert t2.clevel == 2
    assert str(t2) == \
'''fhdr  : BOO
clevel: 2
'''
    assert d.compare_obj(t, t2) == False
    TestField2 = create_nitf_field_structure("TestField2",
        [["fhdr", "", 4, str,  {"default" : "NITF"}],
         ["clevel2", "", 2, int ],
        ])
    t2 = TestField2()
    t2.fhdr = 'FOO'
    t2.clevel2 = 1
    assert d.compare_obj(t, t2) == False

def test_calculated_value(nitf_diff_field_struct):
    '''Test where we have a calculated value, in this case a hard coded value'''
    d = nitf_diff_field_struct # Shorter name
    TestField = create_nitf_field_structure("TestField",
        [["fhdr", "", 4, str],
        ])
    def _fhdr_value(self):
        return "NITF"
    TestField.fhdr_value = _fhdr_value
    t = TestField()
    assert t.fhdr == "NITF"
    with pytest.raises(RuntimeError):
        t.fhdr = 'FOO'
    assert t.fhdr == "NITF"
    assert list(t.items()), (("fhdr", "NITF"))
    assert d.compare_obj(t,t) == True
    
def test_loop(nitf_diff_field_struct):
    '''Test where we have a looping structure'''
    d = nitf_diff_field_struct # Shorter name
    TestField = create_nitf_field_structure("TestField",
        [["fhdr", "", 4, str, {"default" : "NITF"}],
         ["numi", "", 3, int],
         [["loop", "f.numi"],
          ['lish', "", 6, int],
          ['li', "", 10, int]]
        ])
    t = TestField()
    t.numi = 4
    t.lish[0] = 1
    t.lish[1] = 2
    t.lish[2] = 3
    t.lish[3] = 4
    t.li[0] = 5
    t.li[1] = 6
    t.li[2] = 7
    t.li[3] = 8
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
    fh2 = io.BytesIO(b'NITF00200001300000000150000140000000016')
    t2 = TestField()
    t2.read_from_file(fh2)
    assert t2.numi == 2
    assert list(t2.lish) == [13,14]
    assert list(t2.li) == [15,16]
    t2 = copy.deepcopy(t)
    assert d.compare_obj(t, t2) == True
    t2.li[1] = 17
    assert d.compare_obj(t, t2) == False
    
def test_loop_calc_value(nitf_diff_field_struct):
    d = nitf_diff_field_struct # Shorter name
    TestField = create_nitf_field_structure("TestField",
        [["fhdr", "", 4, str, {"default" : "NITF"}],
         ["numi", "", 3, int],
         [["loop", "f.numi"],
          ['lish', "", 6, int],
          ['li', "", 10, int]]
        ])
    def _lish_value(self, i):
        return [11,12,13,14][i]
    def _li_value(self,i):
        return [21,22,23,24][i]
    TestField.lish_value = _lish_value
    TestField.li_value = _li_value
    t = TestField()
    t.numi = 4
    assert list(t.lish) == [11,12,13,14]
    assert list(t.li) == [21,22,23,24]
    with pytest.raises(RuntimeError):
        t.lish[0] = 10
    with pytest.raises(RuntimeError):
        t.li[0] = 10
    assert list(t.items()) == [('fhdr', 'NITF'), ('numi', 4), ('lish', [11, 12, 13, 14]), ('li', [21, 22, 23, 24])]
    assert d.compare_obj(t, t) == True

def test_nested_loop(nitf_diff_field_struct):
    d = nitf_diff_field_struct # Shorter name
    TestField = create_nitf_field_structure("TestField",
        [["fhdr", "", 4, str, {"default" : "NITF"}],
         ["numi", "", 3, int],
         [["loop", "f.numi"],
          ['lish', "", 6, int],
          ["numj", "", 3, int],
          [["loop", "f.numj[i1]"],
           ['li', "", 10, int]]
          ]
        ])
    t = TestField()
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
    t2 = TestField()
    t2.read_from_file(fh2)
    assert str(t) == str(t2)
    assert d.compare_obj(t, t2) == True
    t2.li[1,3] = 17
    assert d.compare_obj(t, t2) == False

def test_nested_loop2(nitf_diff_field_struct):
    d = nitf_diff_field_struct # Shorter name
    # The "mark1" through "mark3" make it easier to look at the write out
    # of the TRE and make sure things are going into the correct spot, and
    # that we are reading this correctly.
    TestField = create_nitf_field_structure("TestField",
        [["fhdr", "", 4, str, {"default" : "NITF"}],
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
        ])
    t = TestField()
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
    t2 = TestField()
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

def test_nested_loop3(nitf_diff_field_struct):
    d = nitf_diff_field_struct # Shorter name
    # The "mark1" through "mark3" make it easier to look at the write out
    # of the TRE and make sure things are going into the correct spot, and
    # that we are reading this correctly.
    TestField = create_nitf_field_structure("TestField",
        [["fhdr", "", 4, str, {"default" : "NITF"}],
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
         ],            
        ])
    t = TestField()
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
    t2 = TestField()
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
    assert FieldValueArray.is_shape_equal(t.li, t2.li)
    assert list(t.li.values()) == list([itm[1] for itm in expected_items])
    assert list(t.li.items()) == expected_items
    assert d.compare_obj(t, t2) == True
    t2.li[1,3,1,0] = 17
    assert d.compare_obj(t, t2) == False
    t2.numl[1,3,1]=t.numl[1,3,1]+1
    assert not FieldValueArray.is_shape_equal(t.li, t2.li)
    assert d.compare_obj(t, t2) == False
    
def test_conditional(nitf_diff_field_struct):
    d = nitf_diff_field_struct # Shorter name
    TestField = create_nitf_field_structure("TestField",
        [["fhdr", "", 4, str, {"default" : "NITF"}],
         ["udhdl", "", 5, int],
         ["udhofl", "", 3, int, {"condition" : "f.udhdl != 0"}],
         ["flttst", "", 10, float, {"condition" : "f.udhdl != 0"}],
        ])
    t = TestField()
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
    TestField = create_nitf_field_structure("TestField",
        [["fhdr", "", 4, str, {"default" : "NITF"}],
         ["numi", "", 3, int],
         [["loop", "f.numi"],
          ["udhdl", "", 5, int],
          ["udhofl", "", 3, int, {"condition" : "f.udhdl[i1] != 0"}]]
         ])
    t = TestField()
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
