from pynitf.priority_handle_set import *
import copy

class PriorityHandleSet1(PriorityHandleSet):
    '''Test class 1'''

class PriorityHandleSet2(PriorityHandleSet):
    '''Test class 2'''
    
def test_priority_set():
    PriorityHandleSet1.add_default_handle("h1")
    PriorityHandleSet1.add_default_handle("h2")
    PriorityHandleSet1.add_default_handle("h1_p10", priority_order=10)
    PriorityHandleSet2.add_default_handle("p2h1_p100", priority_order=100)
    PriorityHandleSet2.add_default_handle("p2h1")
    PriorityHandleSet2.add_default_handle("p2h2")
    PriorityHandleSet2.add_default_handle("p2h1_p10", priority_order=10)
    p2 = copy.copy(PriorityHandleSet2.default_handle_set())
    p2.add_handle("p2h1_p1000", priority_order=1000)
    if(False):
        for (h, p) in PriorityHandleSet1.default_handle_set():
            print(h, p)
    i1 = iter(PriorityHandleSet1.default_handle_set())
    assert(next(i1)[0] == "h1_p10")
    assert(next(i1)[0] in ("h1", "h2"))
    assert(next(i1)[0] in ("h1", "h2"))
    assert(len(PriorityHandleSet1.default_handle_set()) == 3)

    i2 = iter(PriorityHandleSet2.default_handle_set())
    assert(next(i2)[0] == "p2h1_p100")
    assert(next(i2)[0] == "p2h1_p10")
    assert(next(i2)[0] in ("p2h1", "p2h2"))
    assert(next(i2)[0] in ("p2h1", "p2h2"))
    assert(len(PriorityHandleSet2.default_handle_set()) == 4)

    i3 = iter(p2)
    assert(next(i3)[0] == "p2h1_p1000")
    assert(next(i3)[0] == "p2h1_p100")
    assert(next(i3)[0] == "p2h1_p10")
    assert(next(i3)[0] in ("p2h1", "p2h2"))
    assert(next(i3)[0] in ("p2h1", "p2h2"))
    assert(len(p2) == 5)
    
