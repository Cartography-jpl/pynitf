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


# An example of implementing a nonstandard TRE. This depends on having
# lxml available, so we don't have this in the main part of pynitf. But
# we could add this, and in any case this is a nice example of using
# a nonstandard TRE.

class TreILLUMA(Tre):
    __doc__ = '''Sample implementation of xml version of ILLUMA'''
    tre_tag = "ILLUMA"
    field_list = ["solAz", "solEl", "comSolIl",
                  "lunAz", "lunEl", "lunPhAng",
                  "comLunIl", "solLunDisAd", "comTotNaIl",
                  "artIlMin", "artIlMax"]
    def __init__(self):
        for f in self.field_list:
            setattr(self, f, None)
        
    def tre_bytes(self):
        # Can perhaps add in validation with the XLS. But for now, just
        # do a simple xml file
        res = b'<?xml version="1.0" encoding="UTF-8" ?>'
        res += b"<ILLUMA>"
        for f in self.field_list:
            v = getattr(self, f)
            if(v is not None):
                res += f"  <{f}>{v}</{f}>".encode('utf-8')
        res += b"</ILLUMA>"
        return res

    def read_from_tre_bytes(self, bt, nitf_literal=False):
        import xml.etree.ElementTree as ET
        root = ET.fromstring(bt)
        for f in self.field_list:
            n = root.find(f)
            if(n is not None):
                setattr(self, f, float(n.text))
    
    def read_from_file(self, fh, delayed_read=False):
        tag = fh.read(6).rstrip().decode("utf-8")
        if(tag != self.tre_tag):
            raise RuntimeError("Expected TRE %s but got %s" % (self.tre_tag, tag))
        cel = int(fh.read(5))
        self.read_from_tre_bytes(fh.read(cel))

    def __str__(self):
        '''Text description of structure, e.g., something you can print
        out.'''
        res = io.StringIO()
        print("TRE - %s" % self.tre_tag, file=res)
        for f in self.field_list:
            print(f"{f}: {getattr(self,f)}", file=res)
        return res.getvalue()
        
tre_tag_to_cls.add_cls(TreILLUMA)    

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
    

    
