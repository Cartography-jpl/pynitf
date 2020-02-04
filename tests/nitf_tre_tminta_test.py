from pynitf.nitf_tre import *
from pynitf.nitf_tre_tminta import *
from pynitf_test_support import *
import io
    
def test_tre_tminta_basic():

    t = TreTMINTA()

    #Set some values
    t.num_time_int = 2

    t.time_interval_index[0] = 17
    t.start_timestamp[0] = "now"
    t.end_timestamp[0] = "later"

    t.time_interval_index[1] = 42
    t.start_timestamp[1] = "today"
    t.end_timestamp[1] = "tomorrow"

    print (t.summary())

    fh = io.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'TMINTA001120002000017now                     later                   000042today                   tomorrow                '
    
