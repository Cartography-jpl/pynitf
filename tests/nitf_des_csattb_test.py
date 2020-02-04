from pynitf.nitf_des import *
from pynitf.nitf_des_csattb import *
from pynitf.nitf_file import NitfDesSegment, NitfFile
from pynitf_test_support import *
import io

def test_des_snip_user_header():

    ds = DesCSATTB_UH()
    ds.id = '4385ab47-f3ba-40b7-9520-13d6b7a7f311'
    ds.numais = '010'
    for i in range(int(ds.numais)):
        ds.aisdlvl[i] = 5 + i
    ds.reservedsubh_len = 0

    fh_ds = io.BytesIO()
    ds.write_to_file(fh_ds)
    print(fh_ds.getvalue())
    assert fh_ds.getvalue() == b'4385ab47-f3ba-40b7-9520-13d6b7a7f3110100050060070080090100110120130140000000'

    fh2_ds = io.BytesIO(fh_ds.getvalue())
    d2_ds = DesCSATTB_UH()
    d2_ds.read_from_file(fh2_ds)

    assert d2_ds.id == '4385ab47-f3ba-40b7-9520-13d6b7a7f311'
    assert d2_ds.numais == '010'
    for i in range(int(d2_ds.numais)):
        assert d2_ds.aisdlvl[i] == 5 + i
    assert d2_ds.reservedsubh_len == 0

def test_des_csattb_basic():

    d = DesCSATTB()
    d.qual_flag_att = 1
    d.interp_type_att = 1
    d.att_type = 1
    d.eci_ecf_att = 0
    d.dt_att = 900.5
    d.date_att = 20170501
    d.t0_att = 235959.100001000
    d.num_att = 5
    for n in range(d.num_att):
        d.q1[n] = -0.11111
        d.q2[n] = -0.11111
        d.q3[n] = 0.11111
        d.q4[n] = 0.11111
    d.reserved_len = 0
    assert d.user_subheader_size == 46 

    fh = io.BytesIO()
    dseg = NitfDesSegment(des=d);
    hs, ds = dseg.write_to_file(fh, 0, None)
    print(fh.getvalue())
    assert fh.getvalue() == b'DECSATTB                   01U                                                                                                                                                                      0046                                    0  00000001110900.50000000020170501235959.10000100000005-0.111110000000000-0.111110000000000+0.111110000000000+0.111110000000000-0.111110000000000-0.111110000000000+0.111110000000000+0.111110000000000-0.111110000000000-0.111110000000000+0.111110000000000+0.111110000000000-0.111110000000000-0.111110000000000+0.111110000000000+0.111110000000000-0.111110000000000-0.111110000000000+0.111110000000000+0.111110000000000000000000'

    fh2 = io.BytesIO(fh.getvalue())
    dseg2 = NitfDesSegment(header_size=hs, data_size=ds)
    dseg2.read_from_file(fh2)
    d2 = dseg2.des
    assert d2.qual_flag_att == 1
    assert d2.interp_type_att == 1
    assert d2.att_type == 1
    assert d2.eci_ecf_att == 0
    assert d2.dt_att == 900.5
    assert d2.date_att == 20170501
    assert d2.t0_att == 235959.100001000
    assert d2.num_att == 5
    for n in range(d2.num_att):
        assert d2.q1[n] == -0.11111
        assert d2.q2[n] == -0.11111
        assert d2.q3[n] == 0.11111
        assert d2.q4[n] == 0.11111
    assert d2.reserved_len == 0

    print (d2.summary())

def test_des_csattb_uuid_func(isolated_dir):
    d1 = DesCSATTB()
    dseg1 = NitfDesSegment(des=d1);
    d2 = DesCSATTB()
    dseg2 = NitfDesSegment(des=d2);
    d3 = DesCSATTB()
    dseg3 = NitfDesSegment(des=d3);
    dseg1.des.generate_uuid_if_needed()
    dseg2.des.generate_uuid_if_needed()
    dseg3.des.generate_uuid_if_needed()
    id1 = dseg1.des.id
    id2 = dseg2.des.id
    id3 = dseg3.des.id
    dseg1.des.generate_uuid_if_needed()
    assert id1 == dseg1.des.id
    dseg1.des.add_display_level(1)
    dseg1.des.add_display_level(5)
    dseg1.des.add_display_level(1)
    dseg1.des.add_assoc_elem(dseg2.des)
    dseg1.des.add_assoc_elem(dseg3.des)
    f = NitfFile()
    f.des_segment.append(dseg1)
    f.des_segment.append(dseg2)
    f.des_segment.append(dseg3)
    f.write("test.ntf")
    f2 = NitfFile("test.ntf")
    assert(f2.des_segment[0].des.id == id1)
    assert(f2.des_segment[1].des.id == id2)
    assert(f2.des_segment[2].des.id == id3)
    assert(f2.des_segment[0].des.aisdlvl == [1,5])
    assert(f2.des_segment[0].des.assoc_elem_id == [id2, id3])
    assert(f2.des_segment[0].des.assoc_elem(f2) == [f2.des_segment[1].des, f2.des_segment[2].des])
    
    
