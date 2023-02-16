from .nitf_tre import Tre, tre_tag_to_cls

import xml.etree.ElementTree as ET
import io

hlp = '''This is the ILLUMA TRE, Illumination for Spectral Products. 

The field names can be pretty cryptic, but are documented in detail in 
the NGA's SNIP documentation. It is current in draft and is subject to change.

The SNIP documentation is currently not available to the public.

!!! Note that in the current version of ILLUMA you can choose between using traditional fields and using a single
!!! XML file. The conditional flag in choosing between the two is the value of the CEL field in the TRE subheader.
!!! This practice is highly unorthodox and our current pynitf design doesn't easily support this.
!!! For now we will only support the traditional way of using this TRE. Once this TRE is finalized and ratified
!!! by the NTB, we can implement the final version.
'''

desc = [["solAz", "Sun Azimuth Angle", 1, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
        ["solEl", "Sun Elevation Angle", 5, float, {'frmt': '%+05.1f', 'optional': True, 'optional_char' : '-'}],
        ["comSolIl", "Computed Solar Illumination", 5, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
        ["lunAz", "Lunar Azimuth Angle", 5, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
        ["lunEl", "Lunar Elevation Angle", 5, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
        ["lunPhAng", "Phase Angle of the Moon in Degrees", 6, float, {'frmt': '%+06.1f', 'optional': True, 'optional_char' : '-'}],
        ["comLunIl", "Computed Lunar Illumination", 5, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
        ["solLunDisAd", "Solar/Lunar Distance Adjustment", 3, float, {'frmt': '%07f', 'optional': True, 'optional_char' : '-'}],
        ["comTotNaIl", "Computed Total Natural Illumination", 5, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
        ["artIlMin", "Minimum Artificial Illumination", 5, float, {'frmt': '%05f', 'optional': True, 'optional_char' : '-'}],
        ["artIlMax", "Maximum Artificial Illumination", 5, float, {'frmt': '%05f', 'optional': True, 'optional_char' : '-'}],
]

# don't see any sense on having snake and camel case for same thing
# "sol_az"
# "sol_el"
# "com_sol_il"
# "lun_az"
# "lun_el"
# "lun_ph_ang"
# "com_lun_il"
# "sol_lun_dis_ad"
# "com_tot_nat_il"
# "art_ill_min"
# "art_ill_max"


# An example of implementing a nonstandard TRE. This depends on having
# lxml available, so we don't have this in the main part of pynitf. But
# we could add this, and in any case this is a nice example of using
# a nonstandard TRE.

class TreILLUMA(Tre):
    __doc__ = hlp
    desc = desc
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
            descToDict = {field[0]: field for field in desc}
            formatter = descToDict[f][4]['frmt']
            vFormatted = f'{formatter}' % v
            if (vFormatted is not None):
                res += f"  <{f}>{vFormatted}</{f}>".encode('utf-8')
        res += b"</ILLUMA>"
        return res

    def read_from_tre_bytes(self, bt, nitf_literal=False):
        root = ET.fromstring(bt)
        for f in self.field_list:
            n = root.find(f)
            if (n is not None):
                setattr(self, f, float(n.text))

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
        for f in self.field_list:
            print(f"{f}: {getattr(self, f)}", file=res)
        return res.getvalue()


tre_tag_to_cls.add_cls(TreILLUMA)


__all__ = ["TreILLUMA", ]


