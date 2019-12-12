from __future__ import print_function
from .nitf_field import *
from .nitf_security import NitfSecurity

import six

hlp = '''This is a NITF File header. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF File header is described in Table A-1, starting page 66.
'''
desc = [['fhdr', "File Profile Name", 4, str],
        ['fver', "File Version", 5, str],
        ['clevel', "Complexity Level", 2, int, {"default" : 3}],
        ['stype', "Standard Type", 4, str],
        ['ostaid', "Originating Station ID", 10, str],
        ['fdt', "File Data and Time", 14, str],
        ['ftitle', "File Title", 80, str],
        ['fsclas', "File Security Classification", 1, str, {"default" : 'U'}],
        ['fsclsy', "File Classification Security System", 2, str],
        ['fscode', "File Codewords", 11, str],
        ['fsctlh', "File Control and Handling", 2, str],
        ['fsrel', "File Releasing Instructions", 20, str],
        ['fsdctp', "File Declassification Type", 2, str],
        ['fsdcdt', "File Declassification Date", 8, str],
        ['fsdcxm', "File Declassification Exemption", 4, str],
        ['fsdg', "File Downgrade", 1, str],
        ['fsdgdt', "File Downgrade Date", 8, str],
        ['fscltx', "File Classification Text", 43, str],
        ['fscatp', "File Classification Authority Type", 1, str],
        ['fscaut', "File Classification Authority", 40, str],
        ['fscrsn', "File Classification Reason", 1, str],
        ['fssrdt', "File Security Source  Date", 8, str],
        ['fsctln', "File Security Control Number", 15, str],
        ['fscop', "File Copy Number", 5, int],
        ['fscpys', "File Number of Copies", 5, int],
        ['encryp', "Encryption", 1, int],
        ['fbkgc', "", 3, bytes, {"default" : b'\x00\x00\x00'}],
        ['oname', "", 24, str],
        ['ophone', "", 18, str],
        ['fl', "", 12, int],
        ['hl', "", 6, int],
        ['numi', "", 3, int],
        [["loop", "f.numi"],
         ['lish', "", 6, int],
         ['li', "", 10, int]],
        ['nums', "", 3, int],
        [["loop", "f.nums"],
         ['lssh', "", 4, int],
         ['ls', "", 6, int]],
        ['numx', "", 3, int],
        ['numt', "", 3, int],
        [["loop", "f.numt"],
         ['ltsh', "", 4, int],
         ['lt', "", 5, int]],
        ['numdes', "", 3, int],
        [["loop", "f.numdes"],
         ['ldsh', "", 4, int],
         ['ld', "", 9, int]],
        ['numres', "", 3, int],
        [["loop", "f.numres"],
         ['lresh', "", 4, int],
         ['lre', "", 7, int]],
        ['udhdl', "", 5, int],
        ["udhofl", "", 3, int, {"condition" : "f.udhdl != 0"}],
        ['udhd', "", 'f.udhdl', None, {'field_value_class' : FieldData,
                                     'size_offset' : 3}],
        ['xhdl', "", 5, int],
        ["xhdlofl", "", 3, int, {"condition" : "f.xhdl != 0"}],
        ['xhd', "", 'f.xhdl', None, {'field_value_class' : FieldData,
                                     'size_offset' : 3}],
        ]

NitfFileHeader = create_nitf_field_structure("NitfFileHeader", desc, hlp=hlp)
NitfFileHeader.fhdr_value = hardcoded_value("NITF")
NitfFileHeader.fver_value = hardcoded_value("02.10")
NitfFileHeader.stype_value = hardcoded_value("BF01")

def _get_security(self):
    return NitfSecurity.get_security(self, "f")

def _set_security(self, s):
    s.set_security(self, "f")

NitfFileHeader.security = property(_get_security, _set_security)

def summary(self):
    res = six.StringIO()
    print("%s %s %s MD5: " % (self.fhdr, self.fver, self.ftitle), file=res)
    print("%d Image Segments, %d Graphic Segments, %d Text Segments, %d DESs"
          % (self.numi, self.nums, self.numt, self.numdes), file=res)
    return res.getvalue()

NitfFileHeader.summary = summary

__all__ = ["NitfFileHeader"]

