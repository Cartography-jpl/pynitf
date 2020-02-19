from .nitf_field import *
from .nitf_security import NitfSecurity
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
import io

hlp = '''This is a NITF DES subheader. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF DES subheader is described in Table A-8, starting page 112.
'''
des_desc = [['de', "Data Extension Subheader Identifier", 2, str],
        ['desid', "Unique Data Extension Segment Type Identifier", 25, str],
        ['dsver', "Version of the Data Definition", 2, int],
        ['desclas', "Data Extension Segment Security Classification", 1, str],
        ['desclsy', "Data Extension Segment Security Classification System", 2, str],
        ['descode', "DES Codewords", 11, str],
        ['desctlh', "DES Control and Handling", 2, str],
        ['desrel', "DES Release Instructions", 20, str],
        ['desdctp', "DES Declassification Type", 2, str],
        ['desdcdt', "DES Declassification Date", 8, str],
        ['desdcxm', "DES Declassification Exemption", 4, str],
        ['desdg', "DES Downgrade", 1, str],
        ['desdgdt', "DES Downgrade Date", 8, str],
        ['descltx', "DES Classification Text", 43, str],
        ['descatp', "DES Classification Authority Type", 1, str],
        ['descaut', "DES Classification Authority", 40, str],
        ['descrsn', "DES Classification Reason", 1, str],
        ['dessrdt', "DES Security Source Date", 8, str],
        ['desctln', "DES Security Control Number", 15, str],
        ['desoflw', "", 6, str, {"condition" : "f.desid == 'TRE_OVERFLOW'"}],
        ['desitem', "", 3, int, {"condition" : "f.desid == 'TRE_OVERFLOW'"}],
        ['desshl', "DES User-Defined Subheader Length", 4, int],
        ['desshf', "", 'f.desshl', None, {'field_value_class' : FieldData}],
]
NitfDesSubheader = create_nitf_field_structure("NitfDesSubheader", des_desc, hlp=hlp)

NitfDesSubheader.de_value = hardcoded_value("DE")

def summary(self):
    res = io.StringIO()
    print("%s %s %s " % (self.de, self.desid, self.dsver), file=res)
    return res.getvalue()

NitfDesSubheader.summary = summary

def _get_security(self):
    return NitfSecurity.get_security(self, "des")

def _set_security(self, s):
    s.set_security(self, "des")

NitfDesSubheader.security = property(_get_security, _set_security)

# Synonym for desshf so we can have generic handling for user subheader
def _get_user_subheader_data(self):
    return self.desshf

def _set_user_subheader_data(self, v):
    self.desshf = v

NitfDesSubheader.user_subheader_data = property(_get_user_subheader_data,
                                                _set_user_subheader_data)    

class DesSubheaderDiff(FieldStructDiff):
    '''Compare two des subheaders.'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("Des Subheader", {})

    def handle_diff(self, h1, h2, nitf_diff):
        with nitf_diff.diff_context("Subheader", add_text = True):
            if(not isinstance(h1, NitfDesSubheader) or
               not isinstance(h2, NitfDesSubheader)):
                return (False, None)
            if(h1.desid == "TRE_OVERFLOW" and
               h2.desid == "TRE_OVERFLOW"):
                # Skip checking this DES, we already check this when
                # we compare TREs
                return (True, True)
            return (True, self.compare_obj(h1, h2, nitf_diff))

NitfDiffHandleSet.add_default_handle(DesSubheaderDiff())
_default_config = {}
# Ignore all the structural differences about the file. We compare all
# the individual pieces, so this will get reported as we go through each
# element. But it is not useful to also report that udhd varies if we are
# already saying the TREs are different.
_default_config["exclude"] = ['desoflw', 'desitem', 'desshl', 
                              'desshf'] 
 

NitfDiffHandleSet.default_config["Des Subheader"] = _default_config


__all__ = ["NitfDesSubheader"]
