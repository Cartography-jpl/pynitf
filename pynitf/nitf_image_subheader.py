from .nitf_field import FieldStruct, BytesFieldData, FieldStructDiff
from .nitf_security import NitfSecurity
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
import io
import numpy as np
import math

hlp = '''This is a NITF image subheader. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF image subheader is described in Table A-3, starting page 78.
'''

desc = [['im', "File Part Type", 2, str, {"default" : "IM",
                                          "hardcoded_value": True}],
        ['iid1', "Image Identifier 1", 10, str],
        ['idatim', "Image Date and Time", 14, str],
        ['tgtid', "Target Identifier", 17, str],
        ['iid2', "Image Identifier 2", 80, str],
        ['isclas', "Image Security Classification", 1, str, {'default' : 'U'}],
        ['isclsy', "Image Classification Security System", 2, str],
        ['iscode', "Image Codewords", 11, str],
        ['isctlh', "Image Control and Handling", 2, str],
        ['isrel', "Image Release Instructions", 20, str],
        ['isdctp', "Image Declassification Type", 2, str],
        ['isdcdt', "Image Declassification Date", 8, str],
        ['isdcxm', "Image Declassification Exemption", 4, str],
        ['isdg', "Image Downgrade", 1, str],
        ['isdgdt', "Image Downgrade Date", 8, str],
        ['iscltx', "Image Classification Text", 43, str],
        ['iscatp', "Image Classification Authority Type", 1, str],
        ['iscaut', "Image Classification Authority", 40, str],
        ['iscrsn', "Image Classification Reason", 1, str],
        ['issrdt', "Image Security Source Date", 8, str],
        ['isctln', "Image Security Control Number", 15, str],
        ['encryp', "Encryption", 1, int],
        ['isorce', "Image Source", 42, str],
        ['nrows', "Number of Significant Rows in image", 8, int],
        ['ncols', "Number of Significant Columns in image", 8, int],
        ['pvtype', "Pixel Value Type", 3, str, {'default' : 'INT'}],
        ['irep', "Image Representation", 8, str, {'default' : 'MONO'}],
        ['icat', "Image Caetegory", 8, str, {'default' : 'VIS'}],
        ['abpp', "Actual Bits-Per-Pixel Per Band", 2, int, {'default' : 8}],
        ['pjust', "Pixel Justification", 1, str, {'default' : 'R'}],
        ['icords', "Image Coordinate Representation", 1, str],
        ['igeolo', "", 60, str, {'condition' : "f.icords.rstrip() != ''"}],
        ['nicom', "Number of Image Comments", 1, int],
        [["loop", "f.nicom"],
         ["icom", "Image Comments", 80, str]],
        ['ic', "Image Compression", 2, str, {'default' : 'NC'}],
        ['comrat', "", 4, str, {'condition' : "f.ic not in ('NC', 'NM')"}], 
        ['nbands', "Number of Bands", 1, int, {'default' : 1}],
        ['xbands', "", 5, int, {'condition' : "f.nbands == 0"}],
        [["loop", "f.nbands if f.nbands > 0 else f.xbands"],
         ['irepband', "Band Representation", 2, str, {'default' : 'M'}],
         ['isubcat', "Band Subcategory", 6, str],
         ['ifc', "Band Filter Condition", 1, str, {"default" : "N",
                                                   "hardcoded_value": True}],
         ['imflt', "Band Standard Image Filter Code", 3, str,
          {"default" : "   ", "hardcoded_value": True}],
         ['nluts', "Number of LUTS", 1, int],
         ['nelut', "", 5, int, {'condition' : "f.nluts[i1] != 0"}],
         [["loop", "f.nluts[i1]"],
          ['lutd', "", 'f.nelut[i1]', None, {'field_value_class' :
                                             BytesFieldData}]
         ],
        ],
        ['isync', "Image Sync Code", 1, int, {"default" : 0,
                                              "hardcoded_value": True}],
        ['imode', "Image Mode", 1, str, {'default' : 'B'}],
        ['nbpr', "Number of Blocks per Row", 4, int, {'default' : 1 }],
        ['nbpc', "Number of Blocks per Column", 4, int, {'default' : 1}],
        ['nppbh', "Number of Pixels per Block Horizontal", 4, int],
        ['nppbv', "Number of Pixels per Block Vertical", 4, int],
        ['nbpp', "Number of Bits per Pixel", 2, int, {'default' : 8 }],
        ['idlvl', "Image Display Level", 3, int],
        ['ialvl', "Image Attachment Level", 3, int],
        ['iloc', "Image Location", 10, str, {'default' : '0000000000'}],
        ['imag', "Image Magnification", 4, str, {'default' : '1.0'}],
        ['udidl', "User Defined Image Data Length", 5, int],
        ['udofl', "", 3, int, {'condition' : 'f.udidl != 0'}],
        ['udid', "", 'f.udidl', None, {'field_value_class' : BytesFieldData,
                                     'size_offset' : 3}],
        ['ixshdl', "Image Extended Subheader Data Length", 5, int],
        ['ixofl', "", 3, int, {'condition' : 'f.ixshdl != 0'}],
        ['ixshd', "", 'f.ixshdl', None, {'field_value_class' : BytesFieldData,
                                   'size_offset' : 3}]
]

class NitfImageSubheader(FieldStruct):
    __doc__ = help
    desc = desc

    @property
    def security(self):
        return NitfSecurity.get_security(self, "f")

    @security.setter
    def security(self, s):
        s.set_security(self, "f")
        
    def summary(self):
        res = io.StringIO()
        print("%s %s %s" % (self.im, self.iid1, self.iid2), file=res)
        numBands = self.nbands
        if (numBands == 0):
            numBands = self.xbands
        print("%d X %d, %d Band(s), %d/%d bpp"
              % (self.nrows, self.ncols, numBands, self.abpp, self.nbpp),
              file=res)
        return res.getvalue()

    @property
    def number_band(self):
        return (self.nbands if self.nbands > 0 else self.xbands)

    @number_band.setter
    def number_band(self, numband):
        # If the number of bands is < 10, it gets placed in nbands. Otherwise
        #  it is read/written as xbands.
        if (numband < 10):
            self.nbands = numband
        else:
            self.nbands = 0
            self.xbands = numband

    @property
    def dtype(self):
        '''Return the data type. Note that this is always big endian because
        this is what NITF uses. This is the opposite of the native intel format
        (which is little endian).'''
        if(self.nbpp == 8 and self.pvtype == "INT"):
            return np.dtype(np.uint8)
        elif(self.nbpp == 8 and self.pvtype == "SI"):
            return np.dtype(np.int8)
        elif(self.nbpp ==16 and self.pvtype == "INT"):
            return np.dtype('>u2')
        elif(self.nbpp ==16 and self.pvtype == "SI"):
            return np.dtype('>i2')
        elif(self.nbpp ==32 and self.pvtype == "INT"):
            return np.dtype('>u4')
        elif(self.nbpp ==32 and self.pvtype == "SI"):
            return np.dtype('>i4')
        elif(self.nbpp ==32 and self.pvtype == "R"):
            return np.dtype('>f4')
        elif(self.nbpp ==64 and self.pvtype == "C"):
            return np.dtype('>c8')
        elif(self.nbpp ==64 and self.pvtype == "R"):
            return np.dtype('>f8')
        elif(self.nbpp ==128 and self.pvtype == "C"):
            return np.dtype('>c16')
        else:
            raise RuntimeError("Unrecognized nbpp %d and pvtype %s" %
                               (self.nbpp, self.pvtype))

    @dtype.setter
    def dtype(self, data_type):
        '''The data_type should be a numpy type. Note that the NITF image is
        always big endian (the opposite of the intel ordering). Since
        the various read/write classes handle the endian conversion,
        we don't worry here if the data_type is big or little endian,
        so np.dtype('<i2'), np.dtype('i2') and np.dtype('>i2') are all
        treated the same by this function.
    
        Note this results in the weird behavior that blah.dtype = d_type and
        then blah.dtype == d_type might return false (if we converted to big
        endian). I believe this is what we want, but if it turns out that this
        is confusing or a bad idea, then we can revisit this.

        '''
        if (data_type == np.uint8):
            self.abpp = 8
            self.nbpp = 8
            self.pvtype = "INT"
        elif (data_type == np.int8):
            self.abpp = 8
            self.nbpp = 8
            self.pvtype = "SI"
        elif (data_type == np.dtype('<u2') or data_type == np.dtype('>u2')):
            self.abpp = 16
            self.nbpp = 16
            self.pvtype = "INT"
        elif (data_type == np.dtype('<i2') or data_type == np.dtype('>i2')):
            self.abpp = 16
            self.nbpp = 16
            self.pvtype = "SI"
        elif (data_type == np.dtype('<u4') or data_type == np.dtype('>u4')):
            self.abpp = 32
            self.nbpp = 32
            self.pvtype = "INT"
        elif (data_type == np.dtype('<i4') or data_type == np.dtype('>i4')):
            self.abpp = 32
            self.nbpp = 32
            self.pvtype = "SI"
        elif (data_type == np.dtype('<f4') or data_type == np.dtype('>f4')):
            self.abpp = 32
            self.nbpp = 32
            self.pvtype = "R"
        elif (data_type == np.dtype('<c8') or data_type == np.dtype('>c8')):
            self.abpp = 64
            self.nbpp = 64
            self.pvtype = "C"
        elif (data_type == np.dtype('<f8') or data_type == np.dtype('>f8')):
            self.abpp = 64
            self.nbpp = 64
            self.pvtype = "R"
        elif (data_type == np.dtype('<c16') or data_type == np.dtype('>c16')):
            self.abpp = 128
            self.nbpp = 128
            self.pvtype = "C"
        else:
            raise RuntimeError("Unsupported data_type")

    @property
    def geolo_corner(self):
        '''These gets the IGEOLO corners. We return icoords, corners, utm_zone
        as the inverse for _set_geolo_corner.'''
        icoords = self.icords
        corners, utm_zone = nitf_read_igeolo(self.icords,
                                             self.igeolo.encode('utf-8'))
        return icoords, corners, utm_zone
    
    @geolo_corner.setter
    def geolo_corner(self, v):
        '''Set IGEOLO corners. We pass the icoords to specify the encoding,
        the corners, and for UTM the utm_zone. The corners are an array
        of 4 pairs. Each pair is X, Y which is longitude, latitude or UTM
        X, Y. The corners are in the order upper left, upper right, lower right,
        lower left (these are in the image space)'''
        icoords, corners, utm_zone = v
        self.icords = icoords
        self.igeolo = nitf_write_igeolo(icoords, utm_zone,
                                        corners).decode('utf-8')


    @property
    def shape(self):
        return (self.number_band, self.nrows, self.ncols)


# This is GDAL code copied out as python. It is a bit klunky since this is
# C++ rather than python, but we try to stay as close as possible to GDAL since
# it is well tested. This is all hidden in this module, so the klunkiness is
# fine

def check_igeolo_utm_x(name, x):
    t = math.floor(x+0.5)
    if(t < -100000 or t >= 1000000):
        raise RuntimeError("Attempt to write UTM easting %s=%d which is outside the valid range." % (name, t))

def check_igeolo_utm_y(name, y):
    t = math.floor(y+0.5)
    if(t < -1000000 or t >= 10000000):
        raise RuntimeError("Attempt to write UTM northing %s=%d which is outside the valid range." % (name, t))

def nitf_encode_dms_loc(dfValue, pszAxis):
    if(pszAxis == "Lat"):
        chHemisphere = 'S' if dfValue < 0.0 else 'N'
    else:
        chHemisphere = 'W' if dfValue < 0.0 else 'E'
    dfValue = math.fabs(dfValue)
    nDegrees = int(dfValue)
    dfValue = (dfValue-nDegrees) * 60.0
    nMinutes = int(dfValue)
    dfValue = (dfValue-nMinutes) * 60.0
    nSeconds = int(dfValue + 0.5)
    if nSeconds == 60:
    # Do careful rounding on seconds so that 59.9->60 is properly
    # rolled into minutes and degrees.
        nSeconds = 0
        nMinutes += 1
        if nMinutes == 60:
            nMinutes = 0
            nDegrees += 1
    if pszAxis == "Lat":
        res = "%02d%02d%02d%s" % (nDegrees, nMinutes, nSeconds, chHemisphere)
    else:
        res = "%03d%02d%02d%s" % (nDegrees, nMinutes, nSeconds, chHemisphere)
    return res.encode('utf-8')

def test_nitf_encode_dms_loc():
    print(nitf_encode_dms_loc(50 + 30 / 60.0 + 20 / (60 * 60), "Lat"))
    print(nitf_encode_dms_loc(50 + 30 / 60.0 + 20 / (60 * 60), "Lon"))
    print(nitf_encode_dms_loc(-50 + 30 / 60.0 + 20 / (60 * 60), "Lat"))
    print(nitf_encode_dms_loc(-50 + 30 / 60.0 + 20 / (60 * 60), "Lon"))

def nitf_write_igeolo(chICORDS, nZone, df):
    [[dfULX, dfULY], [dfURX, dfURY], [dfLRX, dfLRY], [dfLLX, dfLLY]] = df
    szIGEOLO = bytearray(b' ' * 60)
    # Note we don't support the military grid reference system given by
    # 'U'.
    if chICORDS not in ('G', 'N', 'S', 'D'):
        raise RuntimeError("Invalid ICOORDS value (%s)" % chICORDS)
    if chICORDS == 'G':
        if(math.fabs(dfULX) > 180 or math.fabs(dfURX) > 180 or
           math.fabs(dfLRX) > 180 or math.fabs(dfLLX) > 180 or
           math.fabs(dfULY) > 90 or math.fabs(dfURY) > 90 or
           math.fabs(dfLRY) > 90 or math.fabs(dfLLY) > 90):
            raise RuntimeError("Attempt to write geographic bound outside of legal range.")

        szIGEOLO[0:7] = nitf_encode_dms_loc(dfULY, "Lat" );
        szIGEOLO[7:15] = nitf_encode_dms_loc(dfULX, "Long" );
        szIGEOLO[15:22] = nitf_encode_dms_loc(dfURY, "Lat" );
        szIGEOLO[22:30] = nitf_encode_dms_loc(dfURX, "Long" );
        szIGEOLO[30:37] = nitf_encode_dms_loc(dfLRY, "Lat" );
        szIGEOLO[37:45] = nitf_encode_dms_loc(dfLRX, "Long" );
        szIGEOLO[45:52] = nitf_encode_dms_loc(dfLLY, "Lat" );
        szIGEOLO[52:60] = nitf_encode_dms_loc(dfLLX, "Long" );
    if chICORDS == 'D':
        if(math.fabs(dfULX) > 180 or math.fabs(dfURX) > 180 or
           math.fabs(dfLRX) > 180 or math.fabs(dfLLX) > 180 or
           math.fabs(dfULY) > 90 or math.fabs(dfURY) > 90 or
           math.fabs(dfLRY) > 90 or math.fabs(dfLLY) > 90):
            raise RuntimeError("Attempt to write geographic bound outside of legal range.")
        szIGEOLO[0:15] = ("%+#07.3f%+#08.3f" % (dfULY, dfULX)).encode('utf-8')
        szIGEOLO[15:30] = ("%+#07.3f%+#08.3f" % (dfURY, dfURX)).encode('utf-8')
        szIGEOLO[30:45] = ("%+#07.3f%+#08.3f" % (dfLRY, dfLRX)).encode('utf-8')
        szIGEOLO[45:60] = ("%+#07.3f%+#08.3f" % (dfLLY, dfLLX)).encode('utf-8')
    if chICORDS in ('N', 'S'):
        check_igeolo_utm_x("dfULX", dfULX);
        check_igeolo_utm_y("dfULY", dfULY);
        check_igeolo_utm_x("dfURX", dfURX);
        check_igeolo_utm_y("dfURY", dfURY);
        check_igeolo_utm_x("dfLRX", dfLRX);
        check_igeolo_utm_y("dfLRY", dfLRY);
        check_igeolo_utm_x("dfLLX", dfLLX);
        check_igeolo_utm_y("dfLLY", dfLLY);
        szIGEOLO[0:15] = ("%02d%06d%07d" % (nZone, int(math.floor(dfULY)),
                                 int(math.floor(dfULX)))).encode('utf-8')
        szIGEOLO[15:30] = ("%02d%06d%07d" % (nZone, int(math.floor(dfURY)),
                                 int(math.floor(dfURX)))).encode('utf-8')
        szIGEOLO[30:45] = ("%02d%06d%07d" % (nZone, int(math.floor(dfLRY)),
                                 int(math.floor(dfLRX)))).encode('utf-8')
        szIGEOLO[45:60] = ("%02d%06d%07d" % (nZone, int(math.floor(dfLLY)),
                                 int(math.floor(dfLLX)))).encode('utf-8')
    return szIGEOLO

def nitf_read_igeolo(chICORDS, s):
    # Note we don't support the military grid reference system given by
    # 'U'.
    if chICORDS not in ('G', 'N', 'S', 'D'):
        raise RuntimeError("Invalid ICOORDS value (%s)" % chICORDS)

    res = []
    nZone = None
    for pszCoordPair in (s[0:15], s[15:30], s[30:45], s[45:60]):
        if chICORDS in ("N", "S"):
            nZone = int(pszCoordPair[0:2])
            res.append([float(pszCoordPair[2:8]),
                        float(pszCoordPair[8:15])])
        # Not sure what "C" is, but this is in the GDAL code. Go ahead and
        # include, in case this was some backwards compatibility thing or
        # something like that.
        if chICORDS in ("G", "C"):
            y = (float(pszCoordPair[0:2]) +
                 float(pszCoordPair[2:4]) / 60.0 +
                 float(pszCoordPair[4:6]) / 3600.0)
            if(pszCoordPair[6] in ('s', 'S')):
                y *= -1
            x = (float(pszCoordPair[7:10]) +
                 float(pszCoordPair[10:12]) / 60.0 +
                 float(pszCoordPair[12:14]) / 3600.0)
            if(pszCoordPair[14] in ('w', 'W')):
                x *= -1
            res.append([x,y])
        if chICORDS == "D":
            y = float(pszCoordPair[0:7])
            x = float(pszCoordPair[7:15])
            res.append([x,y])
    return res, nZone


def set_default_image_subheader(ih, nrow, ncol, data_type, numbands=1,
                                iid1 = "Test data",
                                iid2 = "This is sample data.",
                                idatim = "20160101120000",
                                irep="MONO",
                                icat="VIS",
                                idlvl = 0):
    '''This populates an image subheader with some basic data. ih should
    be the image subheader. It is possible this function will go away as we
    learn a bit more about this, but for now we have this function.

    The data_type should be a numpy type. Note that the NITF image is always
    big endian (the opposite of the intel ordering). Since the various read/
    write classes handle the endian conversion, we don't worry here if the
    data_type is big or little endian, so np.dtype('<i2'), np.dtype('i2') and
    np.dtype('>i2') are all treated the same by this function.'''
    ih.iid1 = iid1
    ih.iid2 = iid2
    ih.idlvl = idlvl
    # Should probably add some sort of overall class to handle classification
    # stuff. For now, default to unclassfied
    ih.isclas = "U"
    ih.irep = irep
    ih.icat = icat
    ih.encryp = 0
    ih.idatim = idatim
    ih.nrows = nrow
    ih.ncols = ncol
    ih.nbpr = 1
    ih.nbpc = 1
    ih.nppbh = ncol
    ih.nppbv = nrow
    ih.dtype = data_type
    ih.number_band = numbands 
    ih.ic = "NC"
    ih.nicom = 0

    for b in range(numbands):
        ih.irepband[b] = 'M'
        ih.isubcat[b] = b + 1
        ih.nluts[b] = 0

    # If numbands is 1, we end up with the irepband being "R"
    ih.irepband[numbands - 1] = "B"
    ih.irepband[int(numbands / 2)] = "G"
    ih.irepband[0] = "R"

class ImageSubheaderDiff(FieldStructDiff):
    '''Compare two image subheaders.'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("Image Subheader", {})

    def handle_diff(self, h1, h2, nitf_diff):
        with nitf_diff.diff_context("Subheader", add_text = True):
            if(not isinstance(h1, NitfImageSubheader) or
               not isinstance(h2, NitfImageSubheader)):
                return (False, None)
            return (True, self.compare_obj(h1, h2, nitf_diff))

NitfDiffHandleSet.add_default_handle(ImageSubheaderDiff())
_default_config = {}

# Ignore all the structural differences about the file. We compare all
# the individual pieces, so this will get reported as we go through each
# element. But it is not useful to also report that udhd varies if we are
# already saying the TREs are different.

_default_config["exclude"] = ['udidl', 'udofl', 'udid', 
                              'ixshdl', 'ixofl', 'ixshd'] 
 

NitfDiffHandleSet.default_config["Image Subheader"] = _default_config


__all__ = ["NitfImageSubheader", "set_default_image_subheader",
           "ImageSubheaderDiff"]
