from __future__ import print_function
from .nitf_field import *
import six

hlp = '''This is a NITF DES subheader. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in Table A-8, starting page 112.
'''
des_desc = [['de', "", 2, str],
        ['desid', "", 25, str],
        ['dsver', "", 2, int],
        ['dsclas', "", 1, str],
        ['dsclsy', "", 2, str],
        ['dscode', "", 11, str],
        ['dsctlh', "", 2, str],
        ['dsrel', "", 20, str],
        ['dsdctp', "", 2, str],
        ['dsdcdt', "", 8, str],
        ['dsdcxm', "", 4, str],
        ['dsdg', "", 1, str],
        ['dsdgdt', "", 8, str],
        ['dscltx', "", 43, str],
        ['dscatp', "", 1, str],
        ['dscaut', "", 40, str],
        ['dscrsn', "", 1, str],
        ['dssrdt', "", 8, str],
        ['dsctln', "", 15, str],
        ['desoflw', "", 6, str, {"condition" : "f.desid == 'TRE_OVERFLOW'"}],
        ['desitem', "", 3, int, {"condition" : "f.desid == 'TRE_OVERFLOW'"}],
        ['desshl', "", 4, int],
        ['desshf', "", 'f.desshl', None, {'field_value_class' : FieldData}],
]
NitfDesSubheader = create_nitf_field_structure("NitfDesSubheader", des_desc, hlp=hlp)

NitfDesSubheader.de_value = hardcoded_value("DE")

def summary(self):
    res = six.StringIO()
    print("%s %s %s " % (self.de, self.desid, self.dsver), file=res)
    return res.getvalue()

NitfDesSubheader.summary = summary

__all__ = ["NitfDesSubheader"]
