from __future__ import print_function
from .nitf_field import *

import six

hlp = '''This is a NITF File header. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF File header is described in Table A-1, starting page 66.
'''
desc = [['fhdr', "", 4, str],
        ['fver', "", 5, str],
        ['clevel', "", 2, int, {"default" : 3}],
        ['stype', "", 4, str],
        ['ostaid', "", 10, str],
        ['fdt', "", 14, str],
        ['ftitle', "", 80, str],
        ['fsclas', "", 1, str, {"default" : 'U'}],
        ['fsclsy', "", 2, str],
        ['fscode', "", 11, str],
        ['fsctlh', "", 2, str],
        ['fsrel', "", 20, str],
        ['fsdctp', "", 2, str],
        ['fsdcdt', "", 8, str],
        ['fsdcxm', "", 4, str],
        ['fsdg', "", 1, str],
        ['fsdgdt', "", 8, str],
        ['fscltx', "", 43, str],
        ['fscatp', "", 1, str],
        ['fscaut', "", 40, str],
        ['fscrsn', "", 1, str],
        ['fssrdt', "", 8, str],
        ['fsctln', "", 15, str],
        ['fscop', "", 5, int],
        ['fscpys', "", 5, int],
        ['encryp', "", 1, int],
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
# Will want this calculated
NitfFileHeader.fdt_value = hardcoded_value("20021216151629")

def summary(self):
    res = six.StringIO()
    print("%s %s %s MD5: " % (self.fhdr, self.fver, self.ftitle), file=res)
    print("%d Image Segments, %d Graphic Segments, %d Text Segments, %d DESs"
          % (self.numi, self.nums, self.numt, self.numdes), file=res)
    return res.getvalue()

NitfFileHeader.summary = summary

__all__ = ["NitfFileHeader"]

