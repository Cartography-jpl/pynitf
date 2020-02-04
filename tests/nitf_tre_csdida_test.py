from pynitf.nitf_tre import *
from pynitf.nitf_tre_csdida import *
from pynitf_test_support import *
import io

def test_tre_csdida():

    t = TreCSDIDA()

    # Set some values
    t.day = 12
    t.month = 'MAY'
    t.year = 2019
    t.platform_code = 'AB'
    t.vehicle_id = 11
    t.pass_ = 3
    t.operation = 341
    t.sensor_id = 'CD'
    t.product_id = 'EF'
    t.time = 20190709231159
    t.process_time = 20190709231259
    t.software_version_number = '1.0.0'

    fh = io.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'CSDIDA0007012MAY2019AB1103341CDEF000020190709231159201907092312590001NN1.0.0     '

    fh2 = io.BytesIO(fh.getvalue())
    t2 = TreCSDIDA()
    t2.read_from_file(fh2)
    assert t.day == 12
    assert t.month == 'MAY'
    assert t.year == 2019
    assert t.platform_code == 'AB'
    assert t.vehicle_id == 11
    assert t.pass_ == 3
    assert t.operation == 341
    assert t.sensor_id == 'CD'
    assert t.product_id == 'EF'
    assert t.time == 20190709231159
    assert t.process_time == 20190709231259
    assert t.software_version_number == '1.0.0'

    print (t2.summary())
