from pynitf.nitf_text_subheader import *
from pynitf_test_support import *
import io, six

def test_text_subheader_basic():

    t = NitfTextSubheader()

    t.textid = 'abcdefg'
    t.txtalvl = 1
    t.txtitl = 'ABCDEFG'

    fh = six.BytesIO()
    t.write_to_file(fh)
    assert fh.getvalue() == b'TEabcdefg001              ABCDEFG                                                                                                                                                                                                                                                0   00000'
    fh2 = six.BytesIO(fh.getvalue())
    t2 = NitfTextSubheader()
    t2.read_from_file(fh2)

    assert t2.textid  ==  'abcdefg'
    assert t2.txtalvl == 1
    assert t2.txtitl == 'ABCDEFG'

    print (t.summary())
