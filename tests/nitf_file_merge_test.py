from pynitf.nitf_file import NitfFile
from pynitf.nitf_file_merge import NitfFileMerge
from pynitf.nitf_file_json import NitfFileJson
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
from contextlib import contextmanager

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
    t.engdata[0] = np.array([[277]], dtype = np.int16)
    t.englbl[1] = "TEMP2"
    t.engmtxc[1]=1
    t.engmtxr[1]=1
    t.engdatu[1]="tK"
    t.engdata[1]= np.array([[277.45,],], dtype=np.float32)
    t.englbl[2] = "TEMP3 Wall"
    t.engmtxc[2]=10
    t.engmtxr[2]=1
    t.engdatu[2]="NA"
    t.engdata[2]= "10.7 DEG C"

    return t

def write_zero(d, bstart, lstart, sstart):
    d[:,:] = 0

def write_by_row_p(d, bstart, lstart, sstart):
    #print("sstart", sstart)
    for a in range(d.shape[0]):
        for b in range(d.shape[1]):
            #print(a*20+b*30)
            d[a, b] = a*20+b*30

def create_sample_file(skip_h5_file=False):
    '''This is a duplicate of the NitfFileGen test file. We just use this so we have
    something with enough complexity to test merging with, without needing to use
    an external data source.'''
    # Create the file. We don't supply a name yet, that comes when we actually
    # write

    f = NitfFile()

    # Create a NitfImage source. The particular one we have here just puts all
    # the data into a numpy array, which is nice for testing. We'll probably
    # need to write other image sources (although most things can go to a
    # numpy array, so maybe not).
    img = NitfImageWriteNumpy(10, 10, np.uint8, iid1 = "Image 1", idlvl=5)
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
                                      image_gen_mode=NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_BAND, iid1 = "Image 2", idlvl=6)
    segment2 = NitfImageSegment(img2)
    segment2.tre_list.append(createHISTOA())
    segment2.tre_list.append(createENGRDA())
    f.image_segment.append(segment2)

    img3 = NitfImageWriteNumpy(10, 10, np.uint8, iid1 = "Image 1", idlvl=7)
    for i in range(10):
        for j in range(10):
            img3[0,i,j] = i + j
    segment3 = NitfImageSegment(img3)
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

    rng = np.random.RandomState(2021)
    arr = rng.randn(1000)

    g = h_f.create_group('Base_Group')
    d = g.create_dataset('default', data=arr)

    g.attrs['Date'] = "2020-01-01"
    g.attrs['User'] = 'Me'

    d.attrs['OS'] = os.name
    h_f.close()
    # Because of the creation time in file, we don't get a clean merge.
    # We may write code to work around this, but for now just allow this
    # to skip
    if(not skip_h5_file):
        d_ext.attach_file("mytestfile.hdf5")
        de3 = NitfDesSegment(d_ext)
        f.des_segment.append(de3)

    return f

@contextmanager
def try_merge(fbase, fvara, fvarb, fmerge_expect = None):
    '''Since we do this a few times, this handles trying to do a merge.
    This generates all the input files, then yields with the file names
    for base, variant a, variant b, result.

    If fmerge_expect is supplied, we then run nitf diff on the results
    '''
    fbase.write("base.ntf")
    fvara.write("vara.ntf")
    fvarb.write("varb.ntf")
    for t in ("base", "vara", "varb"):
        subprocess.run(["nitf_json_delta", f"{t}.ntf",
                    "base.ntf",
                    f"{t}_delta.json"], check=True)
    yield "base_delta.json", "vara_delta.json", "varb_delta.json", "merge_delta.json"
    if(fmerge_expect is not None):
        fmerge_expect.write("merge_expect.ntf")
        t = subprocess.run(["nitf_diff", "merge_expect.ntf",
                            "base.ntf",
                            "merge_delta.json"])
        assert t.returncode == 0
        
def test_file_merge(isolated_dir):
    # Requires jsonpickle, which isn't a general requirement for pynitf. So just skip
    # test if we don't have this.
    try:
        import jsonpickle
    except ImportError:
        raise pytest.skip("Requires jsonpickle to run")
    f = create_sample_file()
    f.write("nitf_sample_golden.ntf")
    f = create_sample_file()
    # Make some changes, and we'll write out a "new"
    # nitf file
    f.tre_list[0].angle_to_north = 300
    f.file_header.ftitle = "My delta"
    f.text_segment[0].text.string = "My new string"
    f.image_segment[0].tre_list[0].angle_to_north = 310
    f.image_segment[0].subheader.iid2 = "My new IID2"
    f.write("nitf_sample_new.ntf")

    # The new file and the golden aren't the same.
    print("Results of nitf_diff with new file and old golden. Should be different")
    t = subprocess.run(["nitf_diff", "nitf_sample_new.ntf",
                        "nitf_sample_golden.ntf"])
    assert t.returncode == 1

    # Create a json delta file with all the new stuff in the new file.
    t = subprocess.run(["nitf_json_delta", "nitf_sample_new.ntf",
                        "nitf_sample_golden.ntf",
                        "nitf_sample_golden_delta.json"])
    assert t.returncode == 0

    # Then use the delta file to update the golden file. Should match
    print("Results of nitf_diff with new file and old golden plus json delta file. Should be the same")
    t = subprocess.run(["nitf_diff", "nitf_sample_new.ntf",
                        "nitf_sample_golden.ntf",
                        "nitf_sample_golden_delta.json"])
    assert t.returncode == 0

def test_different_tre_git_merge(isolated_dir):
    '''A simple merge, where we start with a base file and then have
    two different variants updating different TREs. We use a standard
    git merge. This should be a clean case, and is the simplest merge
    we need to do.'''
    fbase = create_sample_file(skip_h5_file=True)
    fvara = create_sample_file(skip_h5_file=True)
    fvarb = create_sample_file(skip_h5_file=True)
    fexpect = create_sample_file(skip_h5_file=True)

    # Variant A updates use00a TRE in first image segment
    fvara.image_segment[0].tre_list[0].angle_to_north = 100

    # Variant B updates use00a TRE in second image segment
    fvarb.image_segment[1].tre_list[0].angle_to_north = 200

    # Expected merge is just both of these updated
    fexpect.image_segment[0].tre_list[0].angle_to_north = 100
    fexpect.image_segment[1].tre_list[0].angle_to_north = 200

    # Try doing merge, using git merge
    with try_merge(fbase, fvara, fvarb, fexpect) as\
         (base_name, a_name, b_name, out_name):
        t = subprocess.run(f"git merge-file -p {a_name} {base_name} {b_name} > {out_name}",
                           shell=True)
        assert t.returncode == 0

def test_conflict_tre_git_merge(isolated_dir):
    '''This is a merge where both variant A and B update the same 
    TRE field. This is a real conflict, and the merge should always
    fail.'''
    fbase = create_sample_file(skip_h5_file=True)
    fvara = create_sample_file(skip_h5_file=True)
    fvarb = create_sample_file(skip_h5_file=True)

    # Variant A updates use00a TRE in first image segment
    fvara.image_segment[0].tre_list[0].angle_to_north = 100

    # Variant B updates same use00a TRE with different value
    fvarb.image_segment[0].tre_list[0].angle_to_north = 200

    # No expected merge
    fexpect = None

    # Try doing merge, using git merge
    with try_merge(fbase, fvara, fvarb, fexpect) as\
         (base_name, a_name, b_name, out_name):
        t = subprocess.run(f"git merge-file -p {a_name} {base_name} {b_name} > {out_name}",
                           shell=True)
        # The return code is the number of conflicts. We expect exactly
        # 1 conflict
        assert t.returncode == 1
        
    
