from pynitf.nitf_tre import *
from pynitf.nitf_tre_csde import *
from test_support import *
import io, six

def test_tre_stdidc_basic():

    t = TreSTDIDC()

    # Set some values
    t.acquisition_date = '20170102090000'
    t.mission = 'abcd          '
    t.pass_ = 'Z1'
    t.op_num = 1
    t.start_segment = 'AA'
    t.repro_num = 0
    t.replay_regen = '000'
    t.start_column = 1
    t.start_row = 1
    t.end_segment = 'AA'
    t.end_column = 1
    t.end_row = 1
    t.country = 'US'
    t.wac = 1866
    t.location = '8959N17959E'

    fh = six.BytesIO()
    t.write_to_file(fh)
    #print(fh.getvalue())
    v = b'STDIDC0008920170102090000abcd          Z1001AA00000 00100001AA00100001US18668959N17959E             '
    assert fh.getvalue() == v

    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreSTDIDC()
    t2.read_from_file(fh2)

    assert t.acquisition_date == '20170102090000'
    assert t.mission == 'abcd'
    assert t.pass_ == 'Z1'
    assert t.op_num == 1
    assert t.start_segment == 'AA'
    assert t.repro_num == 0
    assert t.replay_regen == '000'
    assert t.start_column == 1
    assert t.start_row == 1
    assert t.end_segment == 'AA'
    assert t.end_column == 1
    assert t.end_row == 1
    assert t.country == 'US'
    assert t.wac == 1866
    assert t.location == '8959N17959E'

    print("\n" + t2.summary())
