from __future__ import print_function
from .nitf_field import *
from .nitf_des import *
import six

hlp = '''This is NITF EXT_DEF_CONTENT DES. This is a new DES defined in NSGPDD-A).
'''

desc =["EXT_DEF_CONTENT"]

desc2 =[['content_headers_len', 'Length in bytes of the CONTENT_HEADERS field', 4, int],
        ['content_headers', 'Metadata describing the embedded content', 'f.content_headers_len', None,
          {'field_value_class' : StringFieldData}]]

(DesEXT_DEF_CONTENT, DesEXT_DEF_CONTENT_UH) = create_nitf_des_structure("DesEXT_DEF_CONTENT", desc, desc2, hlp=hlp)

DesEXT_DEF_CONTENT.desid = hardcoded_value("EXT_DEF_CONTENT")
DesEXT_DEF_CONTENT.desver = hardcoded_value("01")

def _summary(self):
    res = six.StringIO()
    return res.getvalue()

DesEXT_DEF_CONTENT.summary = _summary

__all__ = ["DesEXT_DEF_CONTENT", "DesEXT_DEF_CONTENT_UH"]
