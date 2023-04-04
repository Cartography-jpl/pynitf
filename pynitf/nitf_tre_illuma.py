from .nitf_tre import Tre, tre_tag_to_cls

import xml.etree.ElementTree as ET
import io

hlp = '''This is the ILLUMA TRE, Illumination for Spectral Products. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002-1 Appendix AL: ILLUM v1.0).

There was an earlier nonXML version of this TRE, but as far as I can tell
this was never actually adopted. In any case, we only have the XML version of
this as described in Appendix AL.

The SNIP documentation is currently not available to the public.

This class has the attributes (mapping to xml) of:

  sol_az      Sun Azimuth Angle (degrees, 0-360, optional)
  sol_el      Sun Elevation Angle (degrees -90 to 90, optional)
  com_sol_il  Computed Solar Illumination (W m^-2 sr^-1, optional)
  lun_az      Lunar Azimuth Angle (degrees, 0-360, optional)
  lun_el      Lunar Elevation Angle (degrees -90 to 90, optional)
  lun_ph_ang  Phase Angle of the Moon (degrees, -180 to 180, optional)
  com_lun_il  Computed Lunar Illumination (W m^-2 sr^-1, optional)
  sol_lun_dis_ad
              Solar/Lunar Distance Adjustment (optional)
  com_tot_nat_il
             Computed Total Natural Illumination (W m^-2 sr^-1, optional)
  art_il_min Minimum Artificial Illumination (W m^-2 sr^-1, optional)
  art_il_min Maximum Artificial Illumination (W m^-2 sr^-1, optional)
'''

class TreILLUMA(Tre):
    __doc__ = hlp
    tre_tag = "ILLUMA"
    # Field list, as a pair of the XML name and the python attribute going
    # with it
    field_list = [["solAz", "sol_az"],
                  ["solEl", "sol_el"],
                  ["comSolIl", "com_sol_il"],
                  ["lunAz", "lun_az"],
                  ["lunEl", "lun_el"],
                  ["lunPhAng", "lun_ph_ang"],
                  ["comLunIl", "com_lun_il"],
                  ["solLunDisAd", "sol_lun_dis_ad"],
                  ["comTotNaIl", "com_tot_nat_il"],
                  ["artIlMin", "art_il_min"],
                  ["artIlMax", "art_il_max"]]

    def __init__(self):
        for xml_name, attribute_name in self.field_list:
            setattr(self, attribute_name, None)

    def tre_bytes(self):
        # Can perhaps add in validation with the XLS. But for now, just
        # do a simple xml file
        res = b'<?xml version="1.0" encoding="UTF-8" ?>'
        res += b"<ILLUMA>"
        for xml_name, attribute_name in self.field_list:
            val = getattr(self, attribute_name)
            if(val is not None):
                res += f"  <{xml_name}>{val}</{xml_name}>".encode('utf-8')
        res += b"</ILLUMA>"
        return res

    def read_from_tre_bytes(self, bt, nitf_literal=False):
        print(bt)
        root = ET.fromstring(bt)
        for xml_name, attribute_name in self.field_list:
            n = root.find(xml_name)
            if (n is not None):
                setattr(self, attribute_name, float(n.text))

    def read_from_file(self, fh, delayed_read=False):
        tag = fh.read(6).rstrip().decode("utf-8")
        if (tag != self.tre_tag):
            raise RuntimeError("Expected TRE %s but got %s" % (self.tre_tag, tag))
        cel = int(fh.read(5))
        self.read_from_tre_bytes(fh.read(cel))

    def __str__(self):
        '''Text description of structure, e.g., something you can print
        out.'''
        res = io.StringIO()
        print("TRE - %s" % self.tre_tag, file=res)
        for xml_name, attribute_name in self.field_list:
            print(f"{attribute_name}: {getattr(self, attribute_name)}", file=res)
        return res.getvalue()


tre_tag_to_cls.add_cls(TreILLUMA)


__all__ = ["TreILLUMA", ]


