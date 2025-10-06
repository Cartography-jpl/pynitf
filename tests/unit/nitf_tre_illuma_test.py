from pynitf import NitfFile, TreILLUMA
from fixtures.support_func import create_image_seg
import xml.etree.ElementTree as ET
import subprocess
import os
import sys
import pytest
from importlib import util


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
    t2 = f2.image_segment[0].find_one_tre("ILLUMA")
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


def test_nitf_tre_illuma_schema(isolated_dir, xsd_dir):
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
    schema = xmlschema.XMLSchema(xsd_dir / "illuma.xsd")
    root = ET.fromstring(t.tre_bytes())
    schema.validate(root)


def test_nitf_tre_illuma_schema_libxml(isolated_dir, xsd_dir):
    # Sample of using libxml rather than xmlschema.

    try:
        from lxml import etree
    except ImportError:
        pytest.skip("Require xml library to run test")
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
    schema = etree.XMLSchema(etree.parse(xsd_dir / "illuma.xsd"))
    root = etree.fromstring(t.tre_bytes())
    res = schema.validate(root)
    print(res)


# The ILLUMA is a pretty simple XML file to generate. But there may
# be samples of more complicated ones. Here is a stand alone example
# that uses pyxb for generating the xml, which we then validate. This
# can be used as a template
# This test doesn't seems to be working with latest python. I'm guess pyxb
# hasn't been ported to work. Skip for now
@pytest.mark.skip
def test_nitf_tre_illuma_pyxb(isolated_dir, xsd_dir):
    if util.find_spec("pyxb") is None:
        pytest.skip("Require pyxb library to run test")

    subprocess.run(
        [
            "pyxbgen",
            "-u",
            str(xsd_dir / "illuma.xsd"),
            "-m",
            "illuma",
            "--binding-root=./illuma",
        ]
    )
    # Not sure if there is a way to do this directly, but we need
    # to massage this to actually create a module
    subprocess.run("sed -i 's/import _/from . import _/g' illuma/*.py", shell=True)
    subprocess.run("echo 'from .illuma import *' > illuma/__init__.py", shell=True)
    sys.path.append(os.getcwd())
    from illuma import ILLUMA

    sys.path.pop()
    t = ILLUMA()
    t.solAz = 10.0
    t.solEl = 10.0
    with open("sample.xml", "wb") as fh:
        fh.write(t.toxml("utf-8"))
    subprocess.run(["xmllint", "--schema", xsd_dir / "illuma.xsd", "sample.xml"])
    tre = TreILLUMA()
    tre.read_from_tre_bytes(t.toxml("utf-8"))
    print(tre)
