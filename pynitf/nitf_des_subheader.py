from __future__ import print_function
from .nitf_field import *
from .nitf_security import NitfSecurity
import six

hlp = '''This is a NITF DES subheader. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in Table A-8, starting page 112.
'''
des_desc = [['de', "Data Extension Subheader Identifier", 2, str],
        ['desid', "Unique Data Extension Segment Type Identifier", 25, str],
        ['dsver', "Version of the Data Definition", 2, int],
        ['dsclas', "Data Extension Segment Security Classification", 1, str],
        ['dsclsy', "Data Extension Segment Security Classification System", 2, str],
        ['dscode', "DES Codewords", 11, str],
        ['dsctlh', "DES Control and Handling", 2, str],
        ['dsrel', "DES Release Instructions", 20, str],
        ['dsdctp', "DES Declassification Type", 2, str],
        ['dsdcdt', "DES Declassification Date", 8, str],
        ['dsdcxm', "DES Declassification Exemption", 4, str],
        ['dsdg', "DES Downgrade", 1, str],
        ['dsdgdt', "DES Downgrade Date", 8, str],
        ['dscltx', "DES Classification Text", 43, str],
        ['dscatp', "DES Classification Authority Type", 1, str],
        ['dscaut', "DES Classification Authority", 40, str],
        ['dscrsn', "DES Classification Reason", 1, str],
        ['dssrdt', "DES Security Source Date", 8, str],
        ['dsctln', "DES Security Control Number", 15, str],
        ['desoflw', "", 6, str, {"condition" : "f.desid == 'TRE_OVERFLOW'"}],
        ['desitem', "", 3, int, {"condition" : "f.desid == 'TRE_OVERFLOW'"}],
        ['desshl', "DES User-Defined Subheader Length", 4, int],
        ['desshf', "", 'f.desshl', None, {'field_value_class' : FieldData}],
]
NitfDesSubheader = create_nitf_field_structure("NitfDesSubheader", des_desc, hlp=hlp)

NitfDesSubheader.de_value = hardcoded_value("DE")

def summary(self):
    res = six.StringIO()
    print("%s %s %s " % (self.de, self.desid, self.dsver), file=res)
    return res.getvalue()

NitfDesSubheader.summary = summary

def _get_security(self):
    return NitfSecurity.get_security(self, "d")

def _set_security(self, s):
    s.set_security(self, "d")

NitfDesSubheader.security = property(_get_security, _set_security)

__all__ = ["NitfDesSubheader"]
