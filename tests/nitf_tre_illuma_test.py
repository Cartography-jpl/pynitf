from pynitf.nitf_file import NitfFile
from pynitf.nitf_tre import *
from pynitf.nitf_tre_illuma import *
from pynitf_test_support import *
import io

@skip(reason="TRE ILLUMA while likely be dropped in favor of ILLUMB")
def test_tre_illuma_basic():

    t = TreILLUMA()

    # Set some values
    t.sol_az = 180.1
    t.sol_el = -90.0
    t.com_sol_il = 555.6
    t.lun_el = -45.0
    t.lun_ph_ang = +180.0
    t.lun_az = 180.1
    t.com_lun_il = 555.6
    t.com_tot_nat_il = 555.6
    t.sol_lun_dis_ad = 1.1
    t.art_ill_min = '-----'

    fh = io.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'CSCRNA00109Y-90.00000-170.00000+10555.5+09.00000-170.00000+00000.0+90.00000+170.00000+00004.5-09.00000+017.00000-00555.5'

    fh2 = io.BytesIO(fh.getvalue())
    t2 = TreILLUMA()
    t2.read_from_file(fh2)
    assert t2.predict_corners == "Y"

    print (t2.summary())




def test_nitf_tre_illuma_example(isolated_dir):
    f = NitfFile()
    create_image_seg(f)
    t = TreILLUMA()
    t.solAz = 10.0
    t.solEl = 20.0
    t.comSolIl = 50.0
    f.image_segment[0].tre_list.append(t)
    f.write("test.ntf")
    f2=NitfFile("test.ntf")
    print(f2)
    t2 = f2.image_segment[0].find_one_tre('ILLUMA')
    assert t2.solAz == t.solAz
    assert t2.solEl == t.solEl
    assert t2.comSolIl == t.comSolIl
    assert t2.lunPhAng is None
    assert t2.lunAz is None
    assert t2.lunEl is None
    

    
