from pynitf.nitf_tre import *
from pynitf.nitf_tre_rsmecb import *
from pynitf_test_support import *
import io
import pynitf

#pynitf.nitf_field.DEBUG = True
#pynitf.nitf_des.DEBUG = True

def test_rsm_ecb():
    # This test data comes from a GDAL unit test, see https://github.com/OSGeo/gdal/blob/master/autotest/gdrivers/nitf.py
    tre_data = "RSMECB00718iid                                                                             " + \
        "edition                                 tid                                     " + \
        "YY01012020110201GN" + "+9.99999999999999E+99"*6 + "N01ABCD02" + "+9.99999999999999E+99"*3 + \
        "1N2" + "+9.99999999999999E+99"*8 + "N2" + "+9.99999999999999E+99"*4 + "2" + "+9.99999999999999E+99"*4
    fh = io.BytesIO(tre_data.encode('utf8'))
    t = TreRSMECB()
    t.read_from_file(fh)
    t.iid == "iid"
    t.edition == "edition"
    t.tid == "tid"
    t.inclic == "Y"
    t.incluc == "Y"
    t.nparo == 1
    t.ign == 1
    t.cvdate == "20201102"
    t.npar == 1
    t.aptyp == "G"
    t.loctyp == "N"
    t.nsfx == +9.99999999999999E+99
    t.nsfy == +9.99999999999999E+99
    t.nsfx == +9.99999999999999E+99
    t.noffx == +9.99999999999999E+99
    t.noffy == +9.99999999999999E+99
    t.noffz == +9.99999999999999E+99
    t.apbase == "N"
    t.ngsap == 1
    t.gsapid[0] == "ABCD"
    t.numopg[0] == 2
    t.errcvg[0, 0] == +9.99999999999999E+99
    t.errcvg[0, 1] == +9.99999999999999E+99
    t.errcvg[0, 2] == +9.99999999999999E+99
    t.tcdf[0] == 1
    t.acsmc[0] == "N"
    t.ncseg[0] == 2
    t.corseg[0, 0] == +9.99999999999999E+99
    t.corseg[0, 1] == +9.99999999999999E+99
    t.tauseg[0, 0] == +9.99999999999999E+99
    t.tauseg[0, 1] == +9.99999999999999E+99
    t.map[0, 0] == +9.99999999999999E+99
    t.urr == +9.99999999999999E+99
    t.urc == +9.99999999999999E+99
    t.ucc == +9.99999999999999E+99
    t.uacsmc == "N"
    t.uncsr == 2
    t.ucorsr[0] == +9.99999999999999E+99
    t.ucorsr[1] == +9.99999999999999E+99
    t.utausr[0] == +9.99999999999999E+99
    t.utausr[1] == +9.99999999999999E+99
    t.uncsc == 2
    t.ucorsc[0] == +9.99999999999999E+99
    t.ucorsc[1] == +9.99999999999999E+99
    t.utausc[0] == +9.99999999999999E+99
    t.utausc[1] == +9.99999999999999E+99
    print(t)
