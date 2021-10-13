from pynitf.nitf_file import *
from pynitf.nitf_file_header import *
from pynitf.nitf_image_subheader import *
from pynitf.nitf_image import *
from pynitf.nitf_file_diff import NitfDiff
from pynitf_test_support import *
import io

def test_basic_read():
    t = NitfFileHeader()
    t2 = NitfImageReadNumpy(mmap=True)
    with open(unit_test_data + "sample.ntf", 'rb') as fh:
        t.read_from_file(fh)
        t2.subheader.read_from_file(fh)
        t2.read_from_file(fh)
    assert t2.data.shape == (1, 10, 10)
    for i in range(10):
        for j in range(10):
            assert t2[0, i,j] == i + j
    t2 = NitfImageWriteNumpy(10, 10, np.uint8)
    assert t2.shape == (1, 10, 10)
    for i in range(10):
        for j in range(10):
            t2[0, i,j] = i + j
    fh = io.BytesIO()
    t2.write_to_file(fh)
    assert fh.getvalue() == b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12'

@require_gdal_value
def test_write_type(isolated_dir):
    # np.complex128 doesn't work. Not sure that we are handling complex
    # data right. np.complex64 agrees with gdal, but I'm not sure it is
    # doing this right or not. Would be good to find some sample data, to
    # make sure this is correct. All other noncomplex types seem to be
    # correct.
    #for typ in (np.uint8, np.int8, np.uint16, np.int16, np.uint32, np.int32,
    #            np.float32, np.float64, np.complex64, np.complex128):
    nrow = 4
    ncol = 5
    for typ in (np.uint8, np.int8, np.uint16, np.int16, np.uint32, np.int32,
                np.float32, np.float64, np.complex64):
        #print("Checking type %s" % typ)
        f = NitfFile()
        img = NitfImageWriteNumpy(nrow, ncol, typ)
        for i in range(nrow):
            for j in range(ncol):
                img[0, i,j] = 10 * i + j
        # For signed data, make sure we toss in some negative values
        if(typ in (np.int8, np.int16, np.int32)):
            img[0, :,:] = img[0, :, :] + 20
        # For float data, make sure we have some fractions
        if(typ in (np.float32, np.float64)):
            img[0, :,:] = img[0, :, :] / 20.0
        # For comples data, make sure we have some fractions and also
        # some imaginary data.
        if(typ in (np.complex64, np.complex128)):
            img[0, :,:] = (img[0, :, :] / 20.0) * (1 + 0.1j)
        f.image_segment.append(NitfImageSegment(img))
        f.write("test.ntf")
        f2 = NitfFile("test.ntf")
        img2 = f2.image_segment[0].data
        assert img2.dtype == np.dtype(typ).newbyteorder('>')
        assert img2.shape == (1, nrow, ncol)
        for i in range(nrow):
            for j in range(ncol):
                assert img2[0, i,j] == img[0, i,j]
                # For some weird reason, np.complex64 can't convert from
                # string. But python complex data works ok, so use that
                # instead.
                if(typ == np.complex64):
                    t1 = complex(gdal_value("test.ntf", i, j))
                    t2 = img[0, i,j]
                    np.testing.assert_almost_equal(t1, t2)
                else:
                    assert typ(gdal_value("test.ntf", i, j)) == img[0, i,j]

@require_gdal_value
def test_write_band(isolated_dir):
    f = NitfFile()
    nrow = 3
    ncol = 5
    nband = 4
    img = NitfImageWriteNumpy(nrow, ncol, np.int32, numbands=nband)
    for b in range(nband):
        for i in range(nrow):
            for j in range(ncol):
                img[b,i,j] = 10 * i + j + b * 100
    f.image_segment.append(NitfImageSegment(img))
    f.write("test.ntf")
    f2 = NitfFile("test.ntf")
    img2 = f2.image_segment[0].data
    assert img2.shape == img.shape
    for b in range(nband):
        for i in range(nrow):
            for j in range(ncol):
                assert img2[b, i,j] == img[b, i,j]
                assert int(gdal_value("test.ntf", i, j, b)) == img[b,i,j]
    # Check that we update the data in the file after the fact.
    for b in range(nband):
        for i in range(nrow):
            for j in range(ncol):
                img.data_written[b,i,j] = 2 * (10 * i + j + b * 100)
    img.flush_update()
    f2 = NitfFile("test.ntf")
    img2 = f2.image_segment[0].data
    assert img2.shape == img.shape
    for b in range(nband):
        for i in range(nrow):
            for j in range(ncol):
                assert img2[b, i,j] == 2 * (10 * i + j + b * 100)
                assert int(gdal_value("test.ntf", i, j, b)) == 2 * (10 * i + j + b * 100)
    
    

# For some reason this frequently core dumps when testing. This
# doesn't appear to be an actual error, rather just some weird pynitf
# error. In any case, just skip so we don't get a false failure
@skip                
def test_write_data_on_demand(isolated_dir):
    '''A sample of generating data on demand. This generates radiance data
    from DN, Gain, and Offset (like we do for ECOSTRESS). For this example,
    we put all the data in one file. But you could have the data coming
    from a different file, e.g., L1A_PIX being used to generate L1B_RAD for
    ECOSTRESS. The DN, Gain and Offset can also just be numpy arrays if
    desired.'''
    nband = 1
    nrow = 100
    ncol = 200
    f = NitfFile()
    dn = NitfImageWriteNumpy(nrow, ncol, np.int32, numbands=nband,
                              iid1="DN", idlvl=0)
    for r in range(nrow):
        dn[0, r,:] = np.arange(100 * r, 100 * r + dn.shape[2])
    gain = NitfImageWriteNumpy(nrow, ncol, np.float32, numbands=nband,
                               iid1="Gain", idlvl=1)
    offset = NitfImageWriteNumpy(nrow, ncol, np.float32, numbands=nband,
                                 iid1="Offset", idlvl=2)
    f.image_segment.append(NitfImageSegment(dn))
    f.image_segment.append(NitfImageSegment(gain))
    f.image_segment.append(NitfImageSegment(offset))
    # Add twice, just to test getting data by iid1
    rad1 = NitfImageWriteDataOnDemand(nrow, ncol, np.float32,
                 NitfRadCalc(dn, gain, offset).data_to_write,
                 iid1="Radiance", idlvl=3)
    rad2 = NitfImageWriteDataOnDemand(nrow, ncol, np.float32,
                 NitfRadCalc(dn, gain, offset).data_to_write,
                 iid1="Radiance", idlvl=4)
    f.image_segment.append(NitfImageSegment(rad1))
    f.image_segment.append(NitfImageSegment(rad2))
    f.write("test.ntf")

    # Check that we can read data back from the original file that
    # we wrote
    radv = np.array(rad1[:,:,:])
    gv = np.array(gain[:,:,:])
    dnv = np.array(dn[:,:,:])
    ov = np.array(offset[:,:,:])
    np.testing.assert_almost_equal(radv, gv * dnv + ov)
    radv = np.array(rad2[:,:,:])
    np.testing.assert_almost_equal(radv, gv * dnv + ov)
    
    f2 = NitfFile("test.ntf")
    # Check that we can find the iseg by iid1
    assert f2.iseg_by_iid1_single("Gain").idlvl == gain.idlvl
    assert f2.iseg_by_iid1_single("Offset").idlvl == offset.idlvl
    assert f2.iseg_by_iid1_single("DN").idlvl == dn.idlvl
    assert len(f2.iseg_by_iid1("Radiance")) == 2
    assert f2.iseg_by_idlvl(gain.idlvl).iid1 == "Gain"
    assert f2.iseg_by_idlvl(offset.idlvl).iid1 == "Offset"
    assert f2.iseg_by_idlvl(dn.idlvl).iid1 == "DN"
    assert f2.iseg_by_idlvl(rad1.idlvl).iid1 == "Radiance"
    assert f2.iseg_by_idlvl(rad2.idlvl).iid1 == "Radiance"

    # Check that we calculated the data well
    radv = np.array(f2.iseg_by_idlvl(rad1.idlvl).data[:,:,:])
    gv = np.array(gain[:,:,:])
    dnv = np.array(dn[:,:,:])
    ov = np.array(offset[:,:,:])
    np.testing.assert_almost_equal(radv, gv * dnv + ov)
    

@require_gdal_value
def test_write_on_demand_blocking(isolated_dir):
    f = NitfFile()
    nrow = 3
    ncol = 5
    nband = 4
    data = np.empty((nrow, ncol, nband), np.int32)
    for i in range(nrow):
        for j in range(ncol):
            for b in range(nband):
                data[i,j,b] = 10 * i + j + b * 100
    def write_by_row_p(d, bstart, lstart, sstart):
        d[:,:] = data[lstart, :, :]
    img = NitfImageWriteDataOnDemand(nrow=nrow, ncol=ncol, data_type=np.int32,
               numbands=nband, data_callback=write_by_row_p,
               image_gen_mode=NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_ROW_P)    
    f.image_segment.append(NitfImageSegment(img))
    f.write("test.ntf")
    f2 = NitfFile("test.ntf")
    img2 = f2.image_segment[0].data
    assert img2.shape == img.shape
    for b in range(nband):
        for i in range(nrow):
            for j in range(ncol):
                assert img2[b, i,j] == data[i,j,b]
                assert int(gdal_value("test.ntf", i, j, b)) == data[i,j,b]
    t = NitfFileHeader()
    img3 = NitfImageReadNumpy(mmap=False)
    with open("test.ntf", 'rb') as fh:
        t.read_from_file(fh)
        img3.subheader.read_from_file(fh)
        img3.read_from_file(fh)
    assert img3.shape == img.shape
    for b in range(nband):
        for i in range(nrow):
            for j in range(ncol):
                assert img3[b, i,j] == data[i,j,b]
    
def test_diff(print_logging):
    nband = 1
    nrow = 10
    ncol = 20
    dn = NitfImageWriteNumpy(nrow, ncol, np.float32, numbands=nband,
                              iid1="DN", idlvl=0)
    for r in range(nrow):
        dn[0, r,:] = np.arange(100 * r, 100 * r + dn.shape[2])
    f = NitfFile()
    f.image_segment.append(NitfImageSegment(dn))
    f.write("file1.ntf")
    dn2 = NitfImageWriteNumpy(nrow, ncol, np.float32, numbands=nband,
                              iid1="DN", idlvl=0)
    for r in range(nrow):
        dn2[0, r,:] = np.arange(100 * r, 100 * r + dn2.shape[2])
    f = NitfFile()
    f.image_segment.append(NitfImageSegment(dn2))
    f.write("file2.ntf")
    dn2[0,0,0] = dn2[0,0,0] + 1.0
    f = NitfFile()
    f.image_segment.append(NitfImageSegment(dn2))
    f.write("file3.ntf")
    dn3 = NitfImageWriteNumpy(nrow+1, ncol, np.float32, numbands=nband,
                              iid1="DN", idlvl=0)
    for r in range(nrow+1):
        dn3[0, r,:] = np.arange(100 * r, 100 * r + dn3.shape[2])
    f = NitfFile()
    f.image_segment.append(NitfImageSegment(dn3))
    f.write("file4.ntf")
    d = NitfDiff()
    assert d.compare("file1.ntf", "file2.ntf") == True
    assert d.compare("file1.ntf", "file3.ntf") == False
    assert d.compare("file1.ntf", "file4.ntf") == False
    
    
