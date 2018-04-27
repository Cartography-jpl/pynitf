#======================================================================
# Example of creating a simple nitf file
#======================================================================

from pynitf.nitf_file import *
from pynitf.nitf_image import *
from pynitf.nitf_tre_csde import *
from pynitf.nitf_tre_csepha import *
from pynitf.nitf_tre_piae import *
from pynitf.nitf_tre_rpc import *
from pynitf.nitf_tre_geosde import *
from pynitf.nitf_tre_histoa import *
from pynitf.nitf_des_csatta import *
import copy
import json
import six
import numpy as np

def createHISTOA():

    t = TreHISTOA()

    # Set some values
    t.systype = "SYSTEM_TYPE"
    t.pc = "NO_COMPRESSI"
    t.pe = "NONE"
    t.remap_flag = "0"
    t.lutid = 0
    t.nevents = 2

    t.pdate[0] = "2017061512121_"
    t.psite[0] = "ABCDEFGHI_"
    t.pas[0] = "AAAAAAAAA_"
    t.nipcom[0] = 2
    t.ipcom[0, 0] = "HELLO1_"
    t.ipcom[0, 1] = "HELLO2_"

    t.pdate[1] = "20170615121212"
    t.psite[1] = "ABCDEFGHIJ"
    t.pas[1] = "AAAAAAAAAA"
    t.nipcom[1] = 2
    t.ipcom[1, 0] = "HELLO1"
    t.ipcom[1, 1] = "HELLO2"

    return t

def write_zero(d, bstart, lstart, sstart):
    d[:,:,:] = 0

def test_main():
    # Create the file. We don't supply a name yet, that comes when we actually
    # write

    f = NitfFile()

    # Create a NitfImage source. The particular one we have here just puts all
    # the data into a numpy array, which is nice for testing. We'll probably
    # need to write other image sources (although most things can go to a
    # numpy array, so maybe not).
    img = NitfImageWriteNumpy(10, 10, np.uint8)
    for i in range(10):
        for j in range(10):
            img.data[i,j] = i + j

    # We just directly add this to the NitfFile. We need to wrap this as a
    # NitfImageSegment (which adds the subheader). f.image_segment here is
    # just a normal python array.
    f.image_segment.append(NitfImageSegment(img))

    # Create a larger img segment
    img2 = NitfImageWriteDataOnDemand(nrow=3000, ncol=3000, data_type=np.uint8,
                                      numbands=50, data_callback=write_zero,
                                      generate_by_band=True)
    segment2 = NitfImageSegment(img2)
    segment2.tre_list.append(createHISTOA())
    f.image_segment.append(segment2)

    # Can add TRES to either the file or image segment level. This automatically
    # handles TRE overflow, you just put the tre in and the writing figures out
    # where it should go.
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
    t2 = copy.deepcopy(t)
    t2.angle_to_north = 290
    f.tre_list.append(t)
    f.image_segment[0].tre_list.append(t2)

    #Text segment

    d = {
        'first_name': 'Guido',
        'second_name': 'Rossum',
        'titles': ['BDFL', 'Developer'],
    }

    ts = NitfTextSegment(txt = (json.dumps(d)))

    ts.subheader.textid = 'ID12345'
    ts.subheader.txtalvl = 0
    ts.subheader.txtitl = 'sample title'

    f.text_segment.append(ts)

    #DES
    des = DesCSATTA()

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

    data = six.BytesIO()
    des.write_to_file(data)
    de = NitfDesSegment(data = data.getvalue())
    de.subheader.desid = "CSATTA"
    f.des_segment.append(de)

    print (f)

    # Now we write out to a nitf file
    f.write("basic_nitf.ntf")

    # We can also read this back in
    f2 = NitfFile("basic_nitf.ntf")

    # And the actual data (not normally done since most images are too large to
    # print the values
    print("Image Data:")
    print(f2.image_segment[0].data.data)

    print("Text Data:")
    print(f2.text_segment[0].data)

    print("DES Data: ")
    print(f2.des_segment[0].data)

    # We then print out a description of the file
    print(f2.summary())
