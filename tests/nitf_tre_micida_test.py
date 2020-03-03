from pynitf.nitf_tre import *
from pynitf.nitf_tre_micida import *
from pynitf_test_support import *
import io
    
def test_tre_micida_basic():

    t = TreMICIDA()

    #Set some values
    t.num_camera_ids = 2

    t.cameras_id[0] = "First camera ID"
    core_id = b"First core ID"
    t.core_id_length[0] = len(core_id)
    t.camera_core_id[0] = core_id

    t.cameras_id[1] = "Second camera ID"
    core_id = b"Second core ID"
    t.core_id_length[1] = len(core_id)
    t.camera_core_id[1] = core_id

    print (t.summary())

    fh = io.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'MICIDA0011001002First camera ID                     013First core IDSecond camera ID                    014Second core ID'
    
