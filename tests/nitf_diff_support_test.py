from pynitf.nitf_file import *
from pynitf.nitf_tre_csde import *
from pynitf.nitf_tre_csepha import *
from pynitf.nitf_tre_piae import *
from pynitf.nitf_tre_rpc import *
from pynitf.nitf_tre_geosde import *
from pynitf.nitf_des_csatta import *
from pynitf.nitf_image import *
from pynitf.nitf_tre import *
from pynitf_test_support import *
from pynitf.nitf_diff_support import *
import subprocess
import os
import json
import six
import numpy as np
import logging

# Do these in a few places, so collect in one spot.
def create_image_seg(f):
    img = NitfImageWriteNumpy(9, 10, np.uint8)
    for i in range(9):
        for j in range(10):
            img[0, i,j] = i * 10 + j
    f.image_segment.append(NitfImageSegment(img))

def create_tre(f):
    t = TreUSE00A()
    t.angle_to_north = 270
    t.mean_gsd = 105.2
    t.dynamic_range = 2047
    t.obl_ang = 34.12
    t.roll_ang = -21.15
    t.n_ref = 0
    t.rev_num = 3317
    t.n_seg = 1
    t.max_lp_seg = 6287
    t.sun_el = 68.5
    t.sun_az = 131.3
    f.tre_list.append(t)

def create_tre2(f):
    t = TreUSE00A()
    t.angle_to_north = 290
    t.mean_gsd = 105.2
    t.dynamic_range = 2047
    t.obl_ang = 34.12
    t.roll_ang = -21.15
    t.n_ref = 0
    t.rev_num = 3317
    t.n_seg = 1
    t.max_lp_seg = 6287
    t.sun_el = 68.5
    t.sun_az = 131.3
    f.tre_list.append(t)
    
def create_text_segment(f):
    d = {
        'first_name': 'Guido',
        'second_name': 'Rossum',
        'titles': ['BDFL', 'Developer'],
    }
    ts = NitfTextSegment(txt = json.dumps(d))
    ts.subheader.textid = 'ID12345'
    ts.subheader.txtalvl = 0
    ts.subheader.txtitl = 'sample title'
    f.text_segment.append(ts)

def create_des(f):
    des = DesCSATTA()
    des.dsclas = 'U'
    des.att_type = 'ORIGINAL'
    des.dt_att = '900.5000000000'
    des.date_att = 20170501
    des.t0_att = '235959.100001'
    des.num_att = 5
    for n in range(des.num_att):
        des.att_q1[n] = 10.1
        des.att_q2[n] = 10.1
        des.att_q3[n] = 10.1
        des.att_q4[n] = 10.1

    de = NitfDesSegment(des=des)
    f.des_segment.append(de)
    
def test_nitf_diff(isolated_dir):
    '''This create an end to end NITF file, this was at least initially the
    same as basic_nitf_example.py but as a unit test.'''

    # Create the file. We don't supply a name yet, that comes when we actually
    # write
    
    f = NitfFile()
    create_image_seg(f)
    create_tre(f)
    create_tre2(f)
    create_text_segment(f)
    create_des(f)
    f.write("basic_nitf.ntf")
    f.write("basic2_nitf.ntf")
    logger=logging.getLogger("nitf_diff")
    logging.basicConfig(level=logging.DEBUG)
    assert nitf_file_diff("basic_nitf.ntf", "basic2_nitf.ntf")
    
    
