from pynitf.nitf_file import NitfFile
from pynitf.nitf_tre import *
from pynitf.nitf_tre_illuma import *
from pynitf_test_support import *
import xml.etree.ElementTree as ET
import io

def test_nitf_tre_illuma(isolated_dir):
    f = NitfFile()
    create_image_seg(f)
    t = TreILLUMA()

    t.sol_az = 180.09
    t.sol_el = -90.0
    t.com_sol_il = 555.6
    t.lun_az = 180.1
    t.lun_el = -45.0
    t.lun_ph_ang = +180.0
    t.com_lun_il = 555.6
    t.sol_lun_dis_ad = 1.1
    t.com_tot_nat_il = 555.6
    t.art_il_min = 0.0
    t.art_il_max = 50.0
    f.image_segment[0].tre_list.append(t)
    f.write("test.ntf")
    f2 = NitfFile("test.ntf")
    if False:
        print(f2)
    t2 = f2.image_segment[0].find_one_tre('ILLUMA')
    assert t2.sol_az == 180.09
    assert t2.sol_el == -90.0
    assert t2.com_sol_il == 555.6
    assert t2.lun_az == 180.1
    assert t2.lun_el == -45.0
    assert t2.lun_ph_ang == +180.0
    assert t2.com_lun_il == 555.6
    assert t2.sol_lun_dis_ad == 1.1
    assert t2.com_tot_nat_il == 555.6
    assert t2.art_il_min == 0.0
    assert t2.art_il_max == 50.0
    
def test_nitf_tre_illuma_schema(isolated_dir):
    # Note you can also use XMLSchema from libxml. xmlschema seems to give
    # clearer error messages.
    #
    # Even easier if you have this saved to a file, you can use the command
    # line tool xmllint (part of libxml). For example:
    #
    #  xmllint --schema xsd/illuma.xsd sample.xml
    #
    # Requires xmlschema. We don't want to generally require this, so
    # just skip if not  available
    
    try:
        import xmlschema
    except ImportError:
        pytest.skip("Require xmlschema library to run test")
    f = NitfFile()
    create_image_seg(f)
    t = TreILLUMA()

    t.sol_az = 180.09
    t.sol_el = -90.0
    t.com_sol_il = 555.6
    t.lun_az = 180.1
    t.lun_el = -45.0
    t.lun_ph_ang = +180.0
    t.com_lun_il = 555.6
    t.sol_lun_dis_ad = 1.1
    t.com_tot_nat_il = 555.6
    t.art_il_min = 0.0
    t.art_il_max = 50.0
    f.image_segment[0].tre_list.append(t)
    f.write("test.ntf")
    schema = xmlschema.XMLSchema(xsd_dir + "illuma.xsd")
    root=ET.fromstring(t.tre_bytes())
    schema.validate(root)

    
