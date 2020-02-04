from pynitf.nitf_file import NitfFile
from pynitf.nitf_segment_hook import NitfSegmentHook
from pynitf.nitf_tre_csde import TreUSE00A, TreSTDIDC
from pynitf_test_support import *
import io

class SampleObj(object):
    '''Nonsense object used for testing NitfSegmentHook. This just
    combines a couple of fields from two TREs into an object.
    '''
    def __init__(self, angle_to_north, wac):
        self.angle_to_north = angle_to_north
        self.wac = wac
    def __str__(self):
        fh = io.StringIO()
        print("SampleObj:", file=fh)
        print("   angle_to_north: %f" % self.angle_to_north, file=fh)
        print("   wac:            %d" % self.wac, file=fh)
        return fh.getvalue()

class SampleObjHook(NitfSegmentHook):
    def after_init_hook(self, seg, nitf_file):
        seg.sample_obj = None
            
    def after_append_hook(self, seg, nitf_file):
        if(not hasattr(seg, "sample_obj")):
            seg.sample_obj = None
            
    def before_write_hook(self, seg, nitf_file):
        '''Remove all the existing TREs (if any), and add the TREs 
        to store seg.sample_obj'''
        seg.tre_list = [t for t in seg.tre_list if t.tre_tag not in
                        ("USE00A", "STDIDC")]
        if(seg.sample_obj):
            t = TreUSE00A()
            t.angle_to_north = seg.sample_obj.angle_to_north
            seg.tre_list.append(t)
            t = TreSTDIDC()
            t.wac = seg.sample_obj.wac
            seg.tre_list.append(t)
                
    def after_read_hook(self, seg, nitf_file):
        '''Read all the TREs to fill in seg.sample_obj. If there are 
           no TREs, then set seg.sample_obj to None.'''
        # Currently only handle one TRE.
        t1 = seg.find_one_tre('USE00A')
        t2 = seg.find_one_tre('STDIDC')
        if(t1 and t2):
            seg.sample_obj = SampleObj(t1.angle_to_north, t2.wac)
        else:
            seg.sample_obj = None
    def before_str_hook(self, seg, nitf_file, fh):
        '''Called at the start of NitfSegment.__str__'''
        if(seg.sample_obj):
            print(seg.sample_obj, file=fh)
        else:
            print("SampleObj: None", file=fh)
    
    def before_str_tre_hook(self, seg, tre, nitf_file, fh):
        '''Called before printing a TRE. If this returns true we assume
            that this class has handled the TRE printing. Otherwise, we
            call print on the tre'''
        if(seg.sample_obj and tre.tre_tag in ("USE00A", "STDIDC")):
            print("%s: See SampleObj above" % tre.tre_tag, file=fh)
            return True
        return False
    

def test_segment_hook(isolated_dir):
    f = NitfFile()
    iseg = create_image_seg(f)
    t = TreUSE00A()
    t.angle_to_north = 100.0
    iseg.tre_list.append(t)
    t = TreSTDIDC()
    t.wac = 5
    iseg.tre_list.append(t)
    f.write("test.ntf")
    f2 = NitfFile()
    f2.segment_hook_set.add_hook(SampleObjHook())
    f2.read("test.ntf")
    assert(f2.image_segment[0].sample_obj)
    assert(f2.image_segment[0].sample_obj.angle_to_north == 100.0)
    assert(f2.image_segment[0].sample_obj.wac == 5)
    print(f2)
    f3 = NitfFile()
    f3.segment_hook_set.add_hook(SampleObjHook())
    iseg = create_image_seg(f3)
    assert(iseg.sample_obj is None)
    iseg.sample_obj = SampleObj(200.0, 10)
    f3.write("test2.ntf")
    f4 = NitfFile()
    f4.segment_hook_set.add_hook(SampleObjHook())
    f4.read("test2.ntf")
    assert(f4.image_segment[0].sample_obj)
    assert(f4.image_segment[0].sample_obj.angle_to_north == 200.0)
    assert(f4.image_segment[0].sample_obj.wac == 10)
    
