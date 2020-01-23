from pynitf import *
from pynitf_test_support import *

def test_always_true_handle(print_logging):
    '''Basic test where we always match. This tests at the basic mechanics 
    of NitfDiff, and ensures we can add handles to it.'''
    diff = NitfDiff()
    diff.handle_set.add_handle(AlwaysTrueHandle(), priority_order=10000)
    f = NitfFile()
    create_tre(f)
    f.write("basic_nitf.ntf")
    f = NitfFile()
    create_tre(f, 290)
    f.write("basic2_nitf.ntf")
    assert diff.compare("basic_nitf.ntf", "basic2_nitf.ntf") == True

