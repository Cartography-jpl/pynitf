from .nitf_field import FieldStruct, BytesFieldData, FieldStructDiff
from .nitf_security import NitfSecurity
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
import io

hlp = '''This is a NITF text subheader. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF text subheader is described in Table A-6, starting page 107.
'''
desc = [['te', "", 2, str, {"default" : "TE",
                            "hardcoded_value" : True}],
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
        ['tsclas', "", 1, str, {'default' : 'U'}],
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
        ['txshd', "", 'f.txshdl', None, {'field_value_class' : BytesFieldData,
                                   'size_offset' : 3}],
        ]

class NitfTextSubheader(FieldStruct):
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
        print("%s %s %s" % (self.te, self.textid, self.txtitl), file=res)
        return res.getvalue()

class TextSubheaderDiff(FieldStructDiff):
    '''Compare two text subheaders.'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("Text Subheader", {})

    def handle_diff(self, h1, h2, nitf_diff):
        with nitf_diff.diff_context("Subheader", add_text = True):
            if(not isinstance(h1, NitfTextSubheader) or
               not isinstance(h2, NitfTextSubheader)):
                return (False, None)
            return (True, self.compare_obj(h1, h2, nitf_diff))

NitfDiffHandleSet.add_default_handle(TextSubheaderDiff())
_default_config = {}

# Ignore all the structural differences about the file. We compare all
# the individual pieces, so this will get reported as we go through each
# element. But it is not useful to also report that udhd varies if we are
# already saying the TREs are different.

_default_config["exclude"] = ['txshdl', 'txsofl', 'txshd']

NitfDiffHandleSet.default_config["Text Subheader"] = _default_config

__all__ = ["NitfTextSubheader", "TextSubheaderDiff"]
