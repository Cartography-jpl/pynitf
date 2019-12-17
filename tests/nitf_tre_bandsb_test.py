from pynitf.nitf_tre import *
from pynitf.nitf_tre_bandsb import *
from pynitf_test_support import *
import io, six
from struct import *

def test_float_to_fixed_width():
    print(float_to_fixed_width(evil_float1, 7))
    print(len(float_to_fixed_width(evil_float1, 7)))
    print(float_to_fixed_width(evil_float2, 7))
    print(len(float_to_fixed_width(evil_float2, 7)))
    print(float_to_fixed_width(evil_float3, 7, maximum_precision=True))
    print(len(float_to_fixed_width(evil_float3, 7, maximum_precision=True)))

def test_tre_bandsb_basic():

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
    t.existence_mask = 0xFFFFFFC1 #pack('>I',0xFFFFFFC1)
    t.radiometric_adjustment_surface = 'FOCAL PLANE'
    t.atmospheric_adjustment_altitude = 0.0
    t.diameter =  0000.01
    t.data_fld_2 = b'a' * 32
    t.wave_length_unit = 'U'
    for i in range(t.count):
        t.bandid[i] = str(i)
        t.bad_band[i] = 1
        t.niirs[i] = 2.3
        t.focal_len[i] = 22222
        t.cwave[i] = 10000.0
        t.fwhm[i] = 10000.0
        t.fwhm_unc[i] = 10000.0
        t.nom_wave[i] = 10000.0
        t.nom_wave_unc[i] = 10000.0
        t.lbound[i] = evil_float1
        t.ubound[i] = evil_float2
        t.scale_factor[i] = 1.0
        t.additive_factor[i] = 0.0
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
            t.apn_band[i,j] = 7

    for i in range(t.num_aux_c):
        t.capf[i] = 'I'
        t.ucap[i] = 'ABCDEFG'
        t.apn_cube[i] = 8

    print(t)

    fh = six.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'BANDSB0204100005REFLECTANCE             F?\x80\x00\x00\x00\x00\x00\x009999.99M8888.88M7777.77M6666.66Maaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\xff\xff\xff\xc1FOCAL PLANE             \x00\x00\x00\x000000.01aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaU0                                                 12.32222210000.010000.010000.010000.010000.03.141590.00000?\x80\x00\x00\x00\x00\x00\x00180101000000.0011111119999.90.0011111.119999.99M0.010000.00100M0.001111.10.001009999.99M0.001000.00100Maaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa1                                                 12.32222210000.010000.010000.010000.010000.03.141590.00000?\x80\x00\x00\x00\x00\x00\x00180101000000.0011111119999.90.0011111.119999.99M0.010000.00100M0.001111.10.001009999.99M0.001000.00100Maaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa2                                                 12.32222210000.010000.010000.010000.010000.03.141590.00000?\x80\x00\x00\x00\x00\x00\x00180101000000.0011111119999.90.0011111.119999.99M0.010000.00100M0.001111.10.001009999.99M0.001000.00100Maaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa3                                                 12.32222210000.010000.010000.010000.010000.03.141590.00000?\x80\x00\x00\x00\x00\x00\x00180101000000.0011111119999.90.0011111.119999.99M0.010000.00100M0.001111.10.001009999.99M0.001000.00100Maaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa4                                                 12.32222210000.010000.010000.010000.010000.03.141590.00000?\x80\x00\x00\x00\x00\x00\x00180101000000.0011111119999.90.0011111.119999.99M0.010000.00100M0.001111.10.001009999.99M0.001000.00100Maaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa0202IABCDEFG00000000070000000007000000000700000000070000000007IABCDEFG00000000070000000007000000000700000000070000000007IABCDEFG0000000008IABCDEFG0000000008'

    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreBANDSB()
    t2.read_from_file(fh2)

    assert t2.count == 5
    assert t2.radiometric_quantity == 'REFLECTANCE'
    assert t2.radiometric_quantity_unit == 'F'
    assert t2.cube_scale_factor == 1
    assert t2.cube_additive_factor == 0
    assert t2.row_gsd_nrs == str(9999.99)
    assert t2.row_gsd_nrs_unit == 'M'
    assert t2.col_gsd_ncs == str(8888.88)
    assert t2.col_gsd_ncs_unit == 'M'
    assert t2.spt_resp_row_nom == str(7777.77)
    assert t2.spt_resp_unit_row_nom == 'M'
    assert t2.spt_resp_col_nom == str(6666.66)
    assert t2.spt_resp_unit_col_nom == 'M'
    # t.data_fld_1 ==
    assert t2.existence_mask == 0xFFFFFFC1
    assert t2.radiometric_adjustment_surface == 'FOCAL PLANE'
    assert t2.atmospheric_adjustment_altitude == 0
    assert t2.diameter == 0000.01
    # t.data_fld_2 ==
    assert t2.wave_length_unit == 'U'
    for i in range(t2.count):
        assert t2.bandid[i] == str(i)
        assert t2.bad_band[i] == 1
        assert t2.niirs[i] == 2.3
        assert t2.focal_len[i] == 22222
        assert t2.cwave[i] == 10000.0
        assert t2.fwhm[i] == 10000.0
        assert t2.fwhm_unc[i] == 10000.0
        assert t2.nom_wave[i] == 10000.0
        assert t2.nom_wave_unc[i] == 10000.0
        assert_almost_equal (t2.lbound[i], evil_float1, 5)
        assert_almost_equal (t2.ubound[i], evil_float2, 5)
        assert t2.scale_factor[i] == 1
        assert t2.additive_factor[i] == 0
        assert t2.start_time[i] == '180101000000.001'
        assert t2.int_time[i] == 111111
        assert t2.caldrk[i] == 9999.9
        assert t2.calibration_sensitivity[i] == 0.001
        assert t2.row_gsd[i] == 1111.11
        assert t2.row_gsd_unc[i] == 9999.99
        assert t2.row_gsd_unit[i] == 'M'
        assert t2.col_gsd[i] == 0000.01
        assert t2.col_gsd_unc[i] == 000.001
        assert t2.col_gsd_unit[i] == 'M'
        assert t2.bknoise[i] == 0.001
        assert t2.scnnoise[i] == 111.1
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

def test_tre_bandsb_apr():

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

    t.num_aux_b =  2
    t.num_aux_c = 2
    for i in range(t.num_aux_b):
        t.bapf[i] = 'R'
        t.ubap[i] = 'ABCDEFG'
        for j in range(t.count):
            t.apr_band[i,j] = 7

    for i in range(t.num_aux_c):
        t.capf[i] = 'R'
        t.ucap[i] = 'ABCDEFG'
        t.apr_cube[i] = 8

    fh = six.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'BANDSB0020600005REFLECTANCE             F?\x80\x00\x00\x00\x00\x00\x009999.99M8888.88M7777.77M6666.66Maaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\x00\x00\x00\x010202RABCDEFG@\xe0\x00\x00@\xe0\x00\x00@\xe0\x00\x00@\xe0\x00\x00@\xe0\x00\x00RABCDEFG@\xe0\x00\x00@\xe0\x00\x00@\xe0\x00\x00@\xe0\x00\x00@\xe0\x00\x00RABCDEFGA\x00\x00\x00RABCDEFGA\x00\x00\x00'

    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreBANDSB()
    t2.read_from_file(fh2)

    assert t2.count == 5
    assert t2.radiometric_quantity == 'REFLECTANCE'
    assert t2.radiometric_quantity_unit == 'F'
    assert t2.cube_scale_factor == 1
    assert t2.cube_additive_factor == 0
    assert t2.row_gsd_nrs == str(9999.99)
    assert t2.row_gsd_nrs_unit == 'M'
    assert t2.col_gsd_ncs == str(8888.88)
    assert t2.col_gsd_ncs_unit == 'M'
    assert t2.spt_resp_row_nom == str(7777.77)
    assert t2.spt_resp_unit_row_nom == 'M'
    assert t2.spt_resp_col_nom == str(6666.66)
    assert t2.spt_resp_unit_col_nom == 'M'
    # t.data_fld_1 ==
    assert t2.existence_mask == 0x00000001

    for i in range(t2.num_aux_b):
        assert t2.bapf[i] == 'R'
        assert t2.ubap[i] == 'ABCDEFG'
        for j in range(t2.count):
            assert t2.apr_band[i, j] == 7

    for i in range(t2.num_aux_c):
        assert t2.capf[i] == 'R'
        assert t2.ucap[i] == 'ABCDEFG'
        assert t2.apr_cube[i] == 8

    print (t2)

def test_tre_bandsb_snip_sample():
    '''Sample data from SNIP sample file, to check that we can parse 
    this correctly'''
    data = b'00172SPECTRAL RADIANCE       SB\xa0\x00\x00\x00\x00\x00\x000030.00M0030.00M-------M-------M                                                \x89\x80\x00\x00DETECTOR                \x7f\xff\xff\xffU00.851920.0110500.862010.0110500.872100.0110500.882190.0110500.892280.0110500.902360.0110510.912450.0110510.922540.0110510.932640.0110510.942730.0110510.952820.0110510.962910.0110510.972990.0110510.983080.0110510.993170.0110511.003300.0110511.013300.0110511.023400.0110511.033490.0110411.043590.0110411.053690.0110311.063790.0110211.073890.0110111.083990.0110011.094090.0109911.104190.0109711.114190.0109611.124280.0109411.134380.0109211.144480.0109111.154580.0108911.164680.0108711.174770.0108511.184870.0108311.194970.0108211.205070.0108011.215170.0107811.225170.0107711.235270.0107511.245360.0107411.255460.0107311.265560.0107211.275660.0107111.285760.0107011.295860.0107011.305960.0106911.316050.0106911.326050.0106911.336150.0107011.346250.0107111.356350.0107211.366450.0107311.376550.0107411.386650.0107611.396740.0107811.406840.0108011.416940.0108311.426940.0108511.437040.0108811.447140.0109111.457230.0109411.467330.0109711.477430.0110111.487530.0110411.497630.0110811.507730.0111111.517830.0111511.527920.0111811.537920.0112211.548020.0112511.558120.0112811.568220.0113111.578320.0113511.588420.0113811.598510.0114011.608610.0114311.618710.0114511.628810.0114811.638810.0115011.648900.0115111.659000.0115311.669100.0115411.679200.0115511.689300.0115611.699400.0115611.709500.0115611.719600.0115611.729700.0115611.739700.0115511.749790.0115311.759890.0115211.769990.0115011.780090.0114811.790190.0114511.800290.0114311.810380.0114011.820480.0113711.830580.0113411.840580.0113011.850680.0112711.860780.0112411.870870.0112011.880980.0111711.891070.0111311.901170.0111011.911270.0110711.921370.0110411.931470.0110211.941570.0109911.951570.0109711.961660.0109511.971760.0109411.981860.0109211.991960.0109112.002060.0109112.012150.0109112.022250.0109112.032350.0109012.042450.0109012.052450.0108912.062550.0108712.072650.0108612.082750.0108412.092840.0108212.102940.0108012.113040.0107812.123140.0107612.133240.0107312.143340.0107112.153340.0106812.163430.0106612.173530.0106312.183630.0106112.193730.0105812.203830.0105612.213930.0105312.224030.0105112.234120.0104912.244220.0104712.254220.0104612.264320.0104412.274420.0104312.284520.0104212.294610.0104112.304710.0104112.314810.0104112.324910.0104112.335010.0104112.345110.0104112.355210.0104112.365200.0104112.375300.0104112.385400.0104112.395500.0104102.405600.0104102.415700.0104102.425800.0104102.435890.0104102.445990.0104102.456090.0104102.466090.0104102.476190.0104102.486290.0104102.496390.0104102.506480.0104102.516590.0104102.526680.0104102.536780.0104102.546880.0104102.556980.0104102.566980.0104102.577080.01041'
    fh = six.BytesIO()
    fh.write("{:6s}".format('BANDSB').encode("utf-8"))
    fh.write("{:0>5d}".format(len(data)).encode("utf-8"))
    fh.write(data)
    fh2 = six.BytesIO(fh.getvalue())
    t = TreBANDSB()
    t.read_from_file(fh2)
    print(t)

def test_tre_bandsb_minimum():
    '''Minimum set of fields in SNIP v0.1'''
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
    t.existence_mask = 0x99800000
    t.radiometric_adjustment_surface = 'FOCAL PLANE'
    t.atmospheric_adjustment_altitude = 0.0
    t.wave_length_unit = 'U'

    for i in range(t.count):
        t.bandid[i] = str(i)
        t.bad_band[i] = 1
        t.cwave[i] = 10000.0
        t.fwhm[i] = 10000.0

    print(t)

    fh = six.BytesIO()
    t.write_to_file(fh)
    print(fh.getvalue())
    assert fh.getvalue() == b'BANDSB0047600005REFLECTANCE             F?\x80\x00\x00\x00\x00\x00\x009999.99M8888.88M7777.77M6666.66Maaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\x99\x80\x00\x00FOCAL PLANE             \x00\x00\x00\x00U0                                                 110000.010000.01                                                 110000.010000.02                                                 110000.010000.03                                                 110000.010000.04                                                 110000.010000.0'

    fh2 = six.BytesIO(fh.getvalue())
    t2 = TreBANDSB()
    t2.read_from_file(fh2)

    assert t2.count == 5
    assert t2.radiometric_quantity == 'REFLECTANCE'
    assert t2.radiometric_quantity_unit == 'F'
    assert t2.cube_scale_factor == 1
    assert t2.cube_additive_factor == 0
    assert t2.row_gsd_nrs == str(9999.99)
    assert t2.row_gsd_nrs_unit == 'M'
    assert t2.col_gsd_ncs == str(8888.88)
    assert t2.col_gsd_ncs_unit == 'M'
    assert t2.spt_resp_row_nom == str(7777.77)
    assert t2.spt_resp_unit_row_nom == 'M'
    assert t2.spt_resp_col_nom == str(6666.66)
    assert t2.spt_resp_unit_col_nom == 'M'
    # t.data_fld_1 ==
    assert t2.existence_mask == 0x99800000
    assert t2.radiometric_adjustment_surface == 'FOCAL PLANE'
    assert t2.atmospheric_adjustment_altitude == 0
    # t.data_fld_2 ==
    assert t2.wave_length_unit == 'U'
    for i in range(t2.count):
        assert t2.bandid[i] == str(i)
        assert t2.bad_band[i] == 1
        assert t2.cwave[i] == 10000.0
        assert t2.fwhm[i] == 10000.0

    print(t2.summary())
    
    
    
