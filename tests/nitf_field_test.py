from pynitf.nitf_field import *
from test_support import *
import io, six

def test_basic():
    '''Basic test, just set and read values.'''
    TestField = create_nitf_field_structure("TestField",
        [["fhdr", "", 4, str,  {"default" : "NITF"}],
         ["clevel", "", 2, int ],
        ])
    t = TestField()
    assert t.fhdr == "NITF"
    t.fhdr = 'FOO'
    assert t.fhdr == "FOO"
    t.clevel = 1
    fh = six.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'FOO 01'
    fh2 = six.BytesIO(b'BOO 02')
    t2 = TestField()
    t2.read_from_file(fh2)
    assert t2.fhdr == "BOO"
    assert t2.clevel == 2
    assert str(t2) == \
'''fhdr  : BOO
clevel: 2
'''

def test_calculated_value():
    '''Test where we have a calculated value, in this case a hard coded value'''
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

def test_loop():
    '''Test where we have a looping structure'''
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
    fh = six.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF0040000010000000005000002000000000600000300000000070000040000000008'
    fh2 = six.BytesIO(b'NITF00200001300000000150000140000000016')
    t2 = TestField()
    t2.read_from_file(fh2)
    assert t2.numi == 2
    assert list(t2.lish) == [13,14]
    assert list(t2.li) == [15,16]
    
def test_loop_calc_value():
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

def test_nested_loop():
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
    fh = six.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF0020000000030000000000000000001000000000000000000040000000000000000000000000000000000000020' 
    fh2 = six.BytesIO(fh.getvalue())
    t2 = TestField()
    t2.read_from_file(fh2)
    assert str(t) == str(t2)

def test_conditional():
    TestField = create_nitf_field_structure("TestField",
        [["fhdr", "", 4, str, {"default" : "NITF"}],
         ["udhdl", "", 5, int],
         ["udhofl", "", 3, int, {"condition" : "f.udhdl != 0"}]])
    t = TestField()
    with pytest.raises(RuntimeError):
        t.udhofl = 1
    fh = six.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF00000'
    assert t.udhofl is None
    t.udhdl = 10
    t.udhofl = 20
    fh = six.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF00010020'
    assert t.udhofl == 20
    
def test_loop_conditional():
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
    fh = six.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'NITF003000000001003000020040'
    
