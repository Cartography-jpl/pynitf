from __future__ import print_function
from .nitf_field import *

hlp = '''This is a NITF text subheader. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF text subheader is described in Table A-6, starting page 107.
'''
desc = [['te', "", 2, str],
        ['textid', "", 7, str],
        # Note, according to the NITF specification, this should always be
        # present, and if there is no value it should be "000". *However*,
        # digital globe files for ikonos, quickbird, and world view 2 fill
        # this in with all spaces. So we incorrectly mark this as "optional"
        # so we can read these file types, even though this isn't actually
        # valid. For these file, this will return None instead of "000"
        ['txtalvl', "", 3, int, {"optional": True}],
        ['txtdt', "", 14, str],
        ['txtitl', "", 80, str],
        ['tsclas', "", 1, str],
        ['tsclsy', "", 2, str],
        ['tscode', "", 11, str],
        ['tsctlh', "", 2, str],
        ['tsrel', "", 20, str],
        ['tsdctp', "", 2, str],
        ['tsdcdt', "", 8, str],
        ['tsdcxm', "", 4, str],
        ['tsdg', "", 1, str],
        ['tsdgdt', "", 8, str],
        ['tscltx', "", 43, str],
        ['tscatp', "", 1, str],
        ['tscaut', "", 40, str],
        ['tscrsn', "", 1, str],
        ['tssrdt', "", 8, str],
        ['tsctln', "", 15, str],
        ['encryp', "", 1, int],
        ['txtfmt', "", 3, str],
        ['txshdl', "", 5, int],
        ['txsofl', "", 3, int, {'condition' : 'f.txshdl != 0'}],
        ['txshd', "", 'f.txshdl', None, {'field_value_class' : FieldData,
                                   'size_offset' : 3}],
        ]

NitfTextSubheader = create_nitf_field_structure("NitfTextSubheader", desc, hlp=hlp)

NitfTextSubheader.te_value = hardcoded_value("TE")

def _summary(self):
    res = six.StringIO()
    print("%s %s %s" % (self.te, self.textid, self.txtitl), file=res)
    return res.getvalue()

NitfTextSubheader.summary = _summary
