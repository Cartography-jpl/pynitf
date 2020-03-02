from .nitf_field import FieldStruct, BytesFieldData, FieldStructDiff
from .nitf_security import NitfSecurity
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
import io
import numpy as np
import math

hlp = '''This is a NITF graphic subheader. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF graphic subheader is described in Table A-5, starting page 102.
'''

desc = [['sy', "File Part Type", 2, str, {"default" : "SY",
                                          "hardcoded_value" : True}],
        ['sid', "Graphic Identifier", 10, str],
        ['sname', "Graphic name", 20, str],
        ['ssclas', "Graphic Security Classification", 1, str, {'default' : 'U'}],
        ['ssclsy', "Graphic Classification Security System", 2, str],
        ['sscode', "Graphic Codewords", 11, str],
        ['ssctlh', "Graphic Control and Handling", 2, str],
        ['ssrel', "Graphic Release Instructions", 20, str],
        ['ssdctp', "Graphic Declassification Type", 2, str],
        ['ssdcdt', "Graphic Declassification Date", 8, str],
        ['ssdcxm', "Graphic Declassification Exemption", 4, str],
        ['ssdg', "Graphic Downgrade", 1, str],
        ['ssdgdt', "Graphic Downgrade Date", 8, str],
        ['sscltx', "Graphic Classification Text", 43, str],
        ['sscatp', "Graphic Classification Authority Type", 1, str],
        ['sscaut', "Graphic Classification Authority", 40, str],
        ['sscrsn', "Graphic Classification Reason", 1, str],
        ['sssrdt', "Graphic Security Source Date", 8, str],
        ['ssctln', "Graphic Security Control Number", 15, str],
        ['encryp', "Encryption", 1, int],
        ['sfmt', "Graphic Type", 1, str],
        ['sstruct', "Reserved for Future Use", 13, int],
        ['sdlvl', "Graphic Display Level", 3, int],
        ['salvl', "Graphic Attachment Level", 3, int],
        ['sloc', "Graphic Location", 10, str, {'default' : '0000000000'}],
        ['sbnd1', "First Graphic Bound Location", 10, int],
        ['scolor', "Graphic Color", 1, str],
        ['sbnd2', "First Graphic Bound Location", 10, int],
        ['sres2', "Reserved for Future use", 2, int],
        ['sxshdl', "Graphic Extended Subheader Data Length", 5, int],
        ['sxofl', "", 3, int, {'condition' : 'f.sxshdl != 0'}],
        ['sxshd', "", 'f.sxshdl', None, {'field_value_class' : BytesFieldData,
                                   'size_offset' : 3}]
]

class NitfGraphicSubheader(FieldStruct):
    __doc__ = help
    desc = desc

    @property
    def security(self):
        return NitfSecurity.get_security(self, "f")

    @security.setter
    def security(self, s):
        s.set_security(self, "f")
        
    def summary(self):
        res = io.StringIO()
        print("%s %s %s" % (self.sy, self.sid, self.sname), file=res)
        return res.getvalue()


class GraphicSubheaderDiff(FieldStructDiff):
    '''Compare two graphic subheaders.'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("Graphic Subheader", {})

    def handle_diff(self, h1, h2, nitf_diff):
        with nitf_diff.diff_context("Subheader", add_text = True):
            if(not isinstance(h1, NitfGraphicSubheader) or
               not isinstance(h2, NitfGraphicSubheader)):
                return (False, None)
            return (True, self.compare_obj(h1, h2, nitf_diff))

NitfDiffHandleSet.add_default_handle(GraphicSubheaderDiff())
_default_config = {}

# Ignore all the structural differences about the file. We compare all
# the individual pieces, so this will get reported as we go through each
# element. But it is not useful to also report that udhd varies if we are
# already saying the TREs are different.

_default_config["exclude"] = ['sxshdl', 'sxofl', 'sxshd'] 
 

NitfDiffHandleSet.default_config["Graphic Subheader"] = _default_config


__all__ = ["NitfGraphicSubheader",]
