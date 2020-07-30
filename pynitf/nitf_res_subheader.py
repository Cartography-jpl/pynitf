from .nitf_field import FieldStruct, BytesFieldData, FieldStructDiff
from .nitf_security import NitfSecurity
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
import io

hlp = '''This is a NITF RES subheader. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF RES subheader is described in Table A-9, starting page 124.
'''
desc = [['re', "Reserve Extension Subheader Identifier", 2, str,
         {"default" : "RE", "hardcoded_value" : True}],
        ['resid', "Unique Reserve Segment Type Identifier", 25, str],
        ['resver', "Version of the Data Definition", 2, int],
        ['reclas', "Reserve Extension Segment Security Classification", 1, str, {'default' : 'U'}],
        ['reclsy', "Reserve Extension Segment Security Classification System", 2, str],
        ['recode', "RES Codewords", 11, str],
        ['rectlh', "RES Control and Handling", 2, str],
        ['rerel', "RES Release Instructions", 20, str],
        ['redctp', "RES Declassification Type", 2, str],
        ['redcdt', "RES Declassification Date", 8, str],
        ['redcxm', "RES Declassification Exemption", 4, str],
        ['redg', "RES Downgrade", 1, str],
        ['redgdt', "RES Downgrade Date", 8, str],
        ['recltx', "RES Classification Text", 43, str],
        ['recatp', "RES Classification Authority Type", 1, str],
        ['recaut', "RES Classification Authority", 40, str],
        ['recrsn', "RES Classification Reason", 1, str],
        ['resrdt', "RES Security Source Date", 8, str],
        ['rectln', "RES Security Control Number", 15, str],
        ['resshl', "RES User-Defined Subheader Length", 4, int],
        ['resshf', "", 'f.resshl', None, {'field_value_class' :
                                          BytesFieldData}],
]


class NitfResSubheader(FieldStruct):
    __doc__ = help
    desc = desc

    @property
    def security(self):
        return NitfSecurity.get_security(self, "re")

    @security.setter
    def security(self, s):
        s.set_security(self, "re")
        
    def summary(self):
        res = io.StringIO()
        print("%s %s %s " % (self.re, self.resid, self.resver), file=res)
        return res.getvalue()

class ResSubheaderDiff(FieldStructDiff):
    '''Compare two res subheaders.'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("Res Subheader", {})

    def handle_diff(self, h1, h2, nitf_diff):
        with nitf_diff.diff_context("Subheader", add_text = True):
            if(not isinstance(h1, NitfResSubheader) or
               not isinstance(h2, NitfResSubheader)):
                return (False, None)
            return (True, self.compare_obj(h1, h2, nitf_diff))

NitfDiffHandleSet.add_default_handle(ResSubheaderDiff())
_default_config = {}

# Ignore all the structural differences about the file. We compare all
# the individual pieces, so this will get reported as we go through each
# element. But it is not useful to also report that udhd varies if we are
# already saying the TREs are different.

_default_config["exclude"] = ['resshl', 'resshf'] 
 
NitfDiffHandleSet.default_config["Res Subheader"] = _default_config

__all__ = ["NitfResSubheader",]
