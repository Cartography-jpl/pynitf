#======================================================================
# Example of creating a simple nitf file
#======================================================================

from pynitf.nitf_file import NitfFile
from pynitf.nitf_image import NitfImageWriteNumpy, NitfImageWriteDataOnDemand
from pynitf.nitf_tre_csde import TreUSE00A
from pynitf.nitf_tre_histoa import TreHISTOA
from pynitf.nitf_tre_bandsb import TreBANDSB
from pynitf.nitf_tre_engrda import TreENGRDA
from pynitf.nitf_text import NitfTextStr
from pynitf.nitf_des_csattb import DesCSATTB
from pynitf.nitf_des_csephb import DesCSEPHB
from pynitf.nitf_des_ext_def_content import DesEXT_h5
from pynitf_test_support import *
import copy
import json
import numpy as np
import hashlib
import time

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

def createBANDSB():
    t = TreBANDSB()

    t.count = 5
    t.radiometric_quantity = 'REFLECTANCE'
    t.radiometric_quantity_unit = 'F'
    t.cube_scale_factor = 1.0
    t.cube_additive_factor = 0.0
    t.row_gsd_nrs = 9999.99
    t.row_gsd_nrs_unit = 'M'
    t.col_gsd_ncs = 8888.88
    t.col_gsd_ncs_unit = 'M'
    t.spt_resp_row_nom = 7777.77
    t.spt_resp_unit_row_nom = 'M'
    t.spt_resp_col_nom = 6666.66
    t.spt_resp_unit_col_nom = 'M'
    t.data_fld_1 = b'a' * 48
    t.existence_mask = 0x00000001

    t.num_aux_b = 2
    t.num_aux_c = 2
    for i in range(t.num_aux_b):
        t.bapf[i] = 'R'
        t.ubap[i] = 'ABCDEFG'
        for j in range(t.count):
            t.apr_band[i, j] = 7

    for i in range(t.num_aux_c):
        t.capf[i] = 'R'
        t.ucap[i] = 'ABCDEFG'
        t.apr_cube[i] = 8

    return t

def createENGRDA():

    t = TreENGRDA()

    # Set some values
    t.resrc = "My_sensor"
    t.recnt = 3
    t.englbl[0] = b"TEMP1"
    t.engmtxc[0] = 1
    t.engmtxr[0] = 1
    t.engdatu[0] = "tC"
    t.engdata[0] = np.array([[277]], dtype = np.uint16)

    return t

def write_zero(d, bstart, lstart, sstart):
    d[:,:] = 0

def write_by_row_p(d, bstart, lstart, sstart):
    #print("sstart", sstart)
    for a in range(d.shape[0]):
        for b in range(d.shape[1]):
            #print(a*20+b*30)
            d[a, b] = a*20+b*30

def test_main(isolated_dir):
    # Create the file. We don't supply a name yet, that comes when we actually
    # write

    nitf_1 = 'basic_nitf.ntf'
    nitf_2 = 'basic_nitf2.ntf'
    nitf_3 = 'basic_nitf3.ntf'
    nitf_4 = 'basic_nitf4.ntf'    

    f = NitfFile()

    # Create a NitfImage source. The particular one we have here just puts all
    # the data into a numpy array, which is nice for testing. We'll probably
    # need to write other image sources (although most things can go to a
    # numpy array, so maybe not).
    img = NitfImageWriteNumpy(10, 10, np.uint8)
    for i in range(10):
        for j in range(10):
            img[0,i,j] = i + j

    # We just directly add this to the NitfFile. We need to wrap this as a
    # NitfImageSegment (which adds the subheader). f.image_segment here is
    # just a normal python array.
    f.image_segment.append(NitfImageSegment(img))

    # Create a larger img segment
    img2 = NitfImageWriteDataOnDemand(nrow=30, ncol=30, data_type=np.uint8,
                                      numbands=50, data_callback=write_zero,
                                      image_gen_mode=NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_BAND)
    segment2 = NitfImageSegment(img2)
    segment2.tre_list.append(createHISTOA())
    segment2.tre_list.append(createENGRDA())
    f.image_segment.append(segment2)

    # Write by column
    img3 = NitfImageWriteDataOnDemand(nrow=400, ncol=300, data_type=np.dtype('>i2'),
                                      numbands=50, data_callback=write_by_row_p,
                                      image_gen_mode=NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_ROW_P)
    ih = img3.subheader
    ih.nbpr = 300
    ih.nbpc = 1
    ih.nppbh = 1
    ih.nppbv = 400
    ih.imode="P"
    segment3 = NitfImageSegment(img3)
    segment3.tre_list.append(createHISTOA())
    segment3.tre_list.append(createBANDSB())
    f.image_segment.append(segment3)

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

    #Text segment ---------------------------------------------------------------------

    d = {
        'first_name': 'Guido',
        'second_name': 'Rossum',
        'titles': ['BDFL', 'Developer'],
    }

    ts = NitfTextSegment(NitfTextStr(json.dumps(d)))

    ts.subheader.textid = 'ID12345'
    ts.subheader.txtalvl = 0
    ts.subheader.txtitl = 'sample title'

    f.text_segment.append(ts)

    #DES ------------------------------------------------------------------------------

    # -- CSATTB --
    d = DesCSATTB()
    ds = d.user_subheader
    ds.id = '4385ab47-f3ba-40b7-9520-13d6b7a7f311'
    ds.numais = '010'
    for i in range(int(ds.numais)):
        ds.aisdlvl[i] = 5 + i
    ds.reservedsubh_len = 0

    d.qual_flag_att = 1
    d.interp_type_att = 1
    d.att_type = 1
    d.eci_ecf_att = 0
    d.dt_att = 900.5
    d.date_att = 20170501
    d.t0_att = 235959.100001000
    d.num_att = 5
    for n in range(d.num_att):
        d.q1[n] = -0.11111
        d.q2[n] = -0.11111
        d.q3[n] = 0.11111
        d.q4[n] = 0.11111
    d.reserved_len = 0

    de2 = NitfDesSegment(d)
    f.des_segment.append(de2)

    # -- CSEPHB --

    d = DesCSEPHB()
    ds3 = d.user_subheader
    ds3.id = '4385ab47-f3ba-40b7-9520-13d6b7a7f31b'
    ds3.numais = '011'
    for i in range(int(ds3.numais)):
        ds3.aisdlvl[i] = 5 + i
    ds3.reservedsubh_len = 0

    r = 100
    offset1 = 1000
    offset2 = 2000
    d.qual_flag_eph = 1
    d.interp_type_eph = 1
    d.ephem_flag = 1
    d.eci_ecf_ephem = 0
    d.dt_ephem = 900.5
    d.date_ephem = 20170501
    d.t0_ephem = 235959.100001000
    d.num_ephem = r
    for n in range(r):
        d.ephem_x[n] = n * n
        d.ephem_y[n] = n * n + offset1
        d.ephem_z[n] = n * n + offset2
    d.reserved_len = 0

    de3 = NitfDesSegment(d)
    f.des_segment.append(de3)

    # -- EXT_DEF_CONTENT --
    d_ext = DesEXT_h5()
    h_f = h5py.File("mytestfile.hdf5", "w")

    arr = np.random.randn(1000)

    g = h_f.create_group('Base_Group')
    d = g.create_dataset('default', data=arr)

    g.attrs['Date'] = time.time()
    g.attrs['User'] = 'Me'

    d.attrs['OS'] = os.name

    for k in g.attrs.keys():
        print('{} => {}'.format(k, g.attrs[k]))

    for j in d.attrs.keys():
        print('{} => {}'.format(j, d.attrs[j]))

    h_f.close()
    d_ext.attach_file("mytestfile.hdf5")

    de3 = NitfDesSegment(d_ext)
    f.des_segment.append(de3)

    #print (f)

    # Now we write out to a nitf file
    f.write(nitf_1)

    print(os.getcwd())

    # We can also read this back in
    f2 = NitfFile(nitf_1)

    # And the actual data (not normally done since most images are too large to
    # print the values
    print("Image Data:")
    print(f2.image_segment[0].data.data)

    if False:
        bandsb = f2.image_segment[2].tre_list[1]
        assert bandsb.count == 5
        assert bandsb.existence_mask == 0x00000001

    print("Text Data:")
    print(f2.text_segment[0].data)

    assert f2.des_segment[0].subheader.desid == 'CSATTB'
    csattb = f2.des_segment[0].des
    assert csattb.dt_att == 900.5
    assert csattb.date_att == 20170501
    assert csattb.t0_att == 235959.100001000
    csattb_uh = f2.des_segment[0].user_subheader
    assert csattb_uh.id == '4385ab47-f3ba-40b7-9520-13d6b7a7f311'
    assert csattb_uh.numais == '010'
    print(f2.des_segment[0])
    print(csattb)

    assert f2.des_segment[1].subheader.desid == 'CSEPHB'
    csephb = f2.des_segment[1].des
    assert csephb.dt_ephem == 900.5
    assert csephb.date_ephem == 20170501
    assert csephb.t0_ephem == 235959.100001000
    csephb_uh = f2.des_segment[1].user_subheader
    assert csephb_uh.id == '4385ab47-f3ba-40b7-9520-13d6b7a7f31b'
    assert csephb_uh.numais == '011'

    
    assert f2.des_segment[2].subheader.desid == 'EXT_DEF_CONTENT'
    # TODO Come back to this, doesn't currently work
    if(False):
        ext_uh = f2.des_segment[2].user_subheader
        assert ext_uh.content_headers_len == 3
        assert ext_uh.content_headers == b'1:2'

    print (f2.image_segment[2].tre_list)
    assert f2.image_segment[2].find_one_tre("HISTOA") is not None
    assert f2.image_segment[2].find_one_tre("BANDSB") is not None
    assert f2.image_segment[2].find_one_tre("FAKE") is None
    
    # We can't really use NitfImageReadNumpy for blocked data. This special
    # case of writing by row does work, but general blocking doesn't. We'll
    # probably add blocking support with some more direct code (e.g.,
    # GdalMultiBand in GeoCal).
    if(False):
        reshaped_data = f2.image_segment[2].data.data.reshape(300, 400, 50)
        print(reshaped_data[50,:,:])

    # We then print out a description of the file
    #print(f2.summary())
    #print(f2)

    # Write back the file. Two files should be identical
    f2.write("basic_nitf2.ntf")
    md5_1 = hashlib.md5(open(nitf_1,'rb').read()).hexdigest()
    md5_2 = hashlib.md5(open(nitf_2,'rb').read()).hexdigest()
    assert md5_1 == md5_2

    # Write back the file that we just read in after removing an image
    f2.image_segment.remove(f2.image_segment[1])
    f2.write(nitf_3)

    # Simple example of creating a new file, where we just double
    # our input data.
    f = NitfFile(nitf_3)
    f2 = NitfFile()
    img = f.image_segment[0].image
    imgout = NitfImageWriteNumpy(img.shape[1], img.shape[2], img.dtype)
    imgout[:,:] = img[:,:] * 2
    f2.image_segment.append(NitfImageSegment(imgout))
    f2.write(nitf_4)
    f3 = NitfFile(nitf_4)
    img2 = f3.image_segment[0].image
    assert (img2[:,:] == img[:,:] * 2).all()
