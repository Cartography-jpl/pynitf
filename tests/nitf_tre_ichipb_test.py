from pynitf.nitf_tre_ichipb import *
import io

def test_tre_ichipb_basic():
    t = TreICHIPB()

    # Set some values
    t.xfrm_flag = 0
    t.scale_factor = 1.0
    t.anamrph_corr = 1
    t.scanblk_num = 42

    t.op_row_11 = .5
    t.op_col_11 = .5
    t.op_row_12 = .5
    t.op_col_12 = 3.5
    t.op_row_21 = 2.5
    t.op_col_21 = .5
    t.op_row_22 = 2.5
    t.op_col_22 = 3.5

    t.fi_row_11 = 2.5
    t.fi_col_11 = 1.5
    t.fi_row_12 = 2.5
    t.fi_col_12 = 4.5
    t.fi_row_21 = 4.5
    t.fi_col_21 = 1.5
    t.fi_row_22 = 4.5
    t.fi_col_22 = 4.5

    t.fi_row = 9
    t.fi_col = 7

    fh = io.BytesIO()
    t.write_to_file(fh)
    print('getvalue returns:', fh.getvalue())
    assert fh.getvalue() == b'ICHIPB00224000001.00000014200000000.50000000000.50000000000.50000000003.50000000002.50000000000.50000000002.50000000003.50000000002.50000000001.50000000002.50000000004.50000000004.50000000001.50000000004.50000000004.5000000000900000007'


    fh2 = io.BytesIO(fh.getvalue())
    t2 = TreICHIPB()
    t2.read_from_file(fh2)

    fh3 = io.BytesIO()
    t2.write_to_file(fh3)

    assert fh.getvalue() == fh3.getvalue()
    print(t2.summary())
