from pynitf.nitf_tre import *
from pynitf.nitf_tre_bandsb import *
from pynitf_test_support import *
import io, six
from struct import *

@pytest.mark.skip
def test_tre_bandsb_basic():

    t = TreBANDSB()

    t.count = 5
    t.radiometric_quantity = 'REFLECTANCE'
    t.radiometric_quantity_unit = 'F'
    t.cube_scale_factor = pack('>f', 1)
    t.cube_additive_factor = pack('>f', 0)
    t.row_gsd_nrs = 9999.99
    t.row_gsd_nrs_unit = 'M'
    t.col_gsd_ncs = 8888.88
    t.col_gsd_ncs_unit = 'M'
    t.spt_resp_row_nom = 7777.77
    t.spt_resp_unit_row_nom = 'M'
    t.spt_resp_col_nom = 6666.66
    t.spt_resp_unit_col_nom = 'M'
    t.data_fld_1 = b'a' * 48
    t.existence_mask = pack('>I',0xFFFFFFC1)
    t.radiometric_adjustment_surface = 'FOCAL PLANE'
    t.atmospheric_adjustment_altitude = pack('>f', 0)
    t.diameter =  0000.01
    t.data_fld_2 = b'a' * 32
    t.wave_length_unit = 'U'
    for i in range(t.count):
        t.bandid[i] = i
        t.bad_band[i] = 1
        t.niirs[i] = 2.3
        t.focal_len[i] = 22222
        t.cwave[i] = 10000.0
        t.fwhm[i] = 10000.0
        t.fwhm_unc[i] = 10000.0
        t.nom_wave[i] = 10000.0
        t.nom_wave_unc[i] = 10000.0
        t.lbound[i] = 10000.0
        t.ubound[i] = 10000.0
        t.scale_factor[i] = pack('>f', 1)
        t.additive_factor[i] = pack('>f', 0)
        t.start_time[i] = 180101000000.001
        t.int_time[i] = 111111
        t.caldrk[i] = 9999.9
        t.calibration_sensitivity[i] = 0.001
        t.row_gsd[i] = 1111.11
        t.row_gsd_unc[i] = 9999.99
        t.row_gsd_unit[i] = 'M'
        t.col_gsd[i] = 0000.01
        t.col_gsd_unc[i] = 000.001
        t.col_gsd_unit[i] = 'M'
        t.bknoise[i] = 0.001
        t.scnnoise[i] = 111.1
        t.spt_resp_function_row[i] = 000.001
        t.spt_resp_unc_row[i] = 9999.99
        t.spt_resp_unit_row[i] = 'M'
        t.spt_resp_function_col[i] = 000.001
        t.spt_resp_unc_col[i] = 000.001
        t.spt_resp_unit_col[i] = 'M'
        t.data_fld_3[i] = b'a' * 16
        t.data_fld_4[i] = b'a' * 24
        t.data_fld_5[i] = b'a' * 32
        t.data_fld_6[i] = b'a' * 48

    t.num_aux_b =  2
    t.num_aux_c = 2
    for i in range(t.num_aux_b):
        t.bapf[i] = 'I'
        t.ubap[i] = 'ABCDEFG'
        for j in range(t.count):
            t.apn_band[0,0] = 7

    for i in range(t.num_aux_c):
        t.capf[i] = 'I'
        t.ucap[i] = 'ABCDEFG'
        t.apn_cube[i] = 8

    fh = six.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    #assert fh.getvalue() == b''

    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreBANDSB()
    t2.read_from_file(fh2)

    assert t2.count == 5
    assert t2.radiometric_quantity == 'REFLECTANCE'
    assert t2.radiometric_quantity_unit == 'F'
    assert t2.cube_scale_factor == 1
    assert t2.cube_additive_factor == 0
    assert t2.row_gsd_nrs == 9999.99
    assert t2.row_gsd_nrs_unit == 'M'
    assert t2.col_gsd_ncs == 8888.88
    assert t2.col_gsd_ncs_unit == 'M'
    assert t2.spt_resp_row_nom == 7777.77
    assert t2.spt_resp_unit_row_nom == 'M'
    assert t2.spt_resp_col_nom == 6666.66
    assert t2.spt_resp_unit_col_nom == 'M'
    # t.data_fld_1 ==
    assert t2.existence_mask == 0xFFFFFFC1
    assert t2.radiometric_adjustment_surface == 'FOCAL PLANE'
    assert t2.atmospheric_adjustment_altitude == 0
    assert t2.diameter == 0000.01
    # t.data_fld_2 ==
    assert t2.wave_length_unit == 'U'
    for i in range(t2.count):
        assert t2.bandid[i] == i
        assert t2.bad_band[i] == 1
        assert t2.niirs[i] == 2.3
        assert t2.focal_len[i] == 22222
        assert t2.cwave[i] == 10000.0
        assert t2.fwhm[i] == 10000.0
        assert t2.fwhm_unc[i] == 10000.0
        assert t2.nom_wave[i] == 10000.0
        assert t2.nom_wave_unc[i] == 10000.0
        assert t2.lbound[i] == 10000.0
        assert t2.ubound[i] == 10000.0
        assert t2.scale_factor[i] == 1
        assert t2.additive_factor[i] == 0
        assert t2.start_time[i] == 180101000000.001
        assert t2.int_time[i] == 111111
        assert t2.caldrk[i] == 999999
        assert t2.calibration_sensitivity[i] == 0.0001
        assert t2.row_gsd[i] == 1111.11
        assert t2.row_gsd_unc[i] == 9999.99
        assert t2.row_gsd_unit[i] == 'M'
        assert t2.col_gsd[i] == 0000.01
        assert t2.col_gsd_unc[i] == 000.001
        assert t2.col_gsd_unit[i] == 'M'
        assert t2.bknoise[i] == 99999
        assert t2.scnnoise[i] == 11111
        assert t2.spt_resp_function_row[i] == 000.001
        assert t2.spt_resp_unc_row[i] == 9999.99
        assert t2.spt_resp_unit_row[i] == 'M'
        assert t2.spt_resp_function_col[i] == 000.001
        assert t2.spt_resp_unc_col[i] == 000.001
        assert t2.spt_resp_unit_col[i] == 'M'
        # t.data_fld_3 ==
        # t.data_fld_4 ==
        # t.data_fld_5 ==
        # t.data_fld_6 ==

        assert t2.num_aux_b == 2
        assert t2.num_aux_c == 2
    for i in range(t2.num_aux_b):
        assert t2.bapf[i] == 'I'
        assert t2.ubap[i] == 'ABCDEFG'
        for j in range(t2.count):
            assert t2.apn_band[i, j] == 7

    for i in range(t2.num_aux_c):
        assert t2.capf[i] == 'I'
        assert t2.ucap[i] == 'ABCDEFG'
        assert t2.apn_cube[i] == 8

    print (t2.summary())

