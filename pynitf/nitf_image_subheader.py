from __future__ import print_function
from .nitf_field import *
from .nitf_security import NitfSecurity
import six
import numpy as np

hlp = '''This is a NITF image subheader. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF image subheader is described in Table A-3, starting page 78.
'''

def eq_string_ignore_case(s1, s2):
    return s1.casefold() == s2.casefold()
    
desc = [['im', "File Part Type", 2, str],
        ['iid1', "Image Identifier 1", 10, str, {'eq_fun' : (eq_string_ignore_case,), 'name' : 'image.iid1'}],
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
         ['ifc', "Band Filter Condition", 1, str],
         ['imflt', "Band Standard Image Filter Code", 3, str],
         ['nluts', "Number of LUTS", 1, int],
         ['nelut', "", 5, int, {'condition' : "f.nluts[i1] != 0"}],
         [["loop", "f.nluts[i1]"],
          ['lutd', "", 'f.nelut[i1]', None, {'field_value_class' : FieldData}]
         ],
        ],
        ['isync', "Image Sync Code", 1, int],
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
        ['udid', "", 'f.udidl', None, {'field_value_class' : FieldData,
                                     'size_offset' : 3}],
        ['ixshdl', "Image Extended Subheader Data Length", 5, int],
        ['ixofl', "", 3, int, {'condition' : 'f.ixshdl != 0'}],
        ['ixshd', "", 'f.ixshdl', None, {'field_value_class' : FieldData,
                                   'size_offset' : 3}]
]

NitfImageSubheader = create_nitf_field_structure("NitfImageSubheader", desc,
                                                 hlp=hlp)

NitfImageSubheader.im_value = hardcoded_value("IM")
NitfImageSubheader.ifc_value = hardcoded_value("N")
NitfImageSubheader.imflt_value = hardcoded_value("   ")
NitfImageSubheader.isync_value = hardcoded_value(0)

def _summary(self):
    res = six.StringIO()
    print("%s %s %s" % (self.im, self.iid1, self.iid2), file=res)
    numBands = self.nbands
    if (numBands == 0):
        numBands = self.xbands
    print("%d X %d, %d Band(s), %d/%d bpp"
          % (self.nrows, self.ncols, numBands, self.abpp, self.nbpp), file=res)
    return res.getvalue()

NitfImageSubheader.summary = _summary

def _number_band(self):
    return (self.nbands if self.nbands > 0 else self.xbands)

def _set_number_band(self, numband):
    if (numband < 10):
        self.nbands = numband
    else:
        self.nbands = 0
        self.xbands = numband

# If the number of bands is < 10, it gets placed in nbands. Otherwise it
# is read/written as xbands.

NitfImageSubheader.number_band = property(_number_band, _set_number_band)

def _dtype(ih):
    '''Return the data type. Note that this is always big endian because
    this is what NITF uses. This is the opposite of the native intel format
    (which is little endian).'''
    if(ih.nbpp == 8 and ih.pvtype == "INT"):
        return np.dtype(np.uint8)
    elif(ih.nbpp == 8 and ih.pvtype == "SI"):
        return np.dtype(np.int8)
    elif(ih.nbpp ==16 and ih.pvtype == "INT"):
        return np.dtype('>u2')
    elif(ih.nbpp ==16 and ih.pvtype == "SI"):
        return np.dtype('>i2')
    elif(ih.nbpp ==32 and ih.pvtype == "INT"):
        return np.dtype('>u4')
    elif(ih.nbpp ==32 and ih.pvtype == "SI"):
        return np.dtype('>i4')
    elif(ih.nbpp ==32 and ih.pvtype == "R"):
        return np.dtype('>f4')
    elif(ih.nbpp ==64 and ih.pvtype == "C"):
        return np.dtype('>c8')
    elif(ih.nbpp ==64 and ih.pvtype == "R"):
        return np.dtype('>f8')
    elif(ih.nbpp ==128 and ih.pvtype == "C"):
        return np.dtype('>c16')
    else:
        raise RuntimeError("Unrecognized nbpp %d and pvtype %s" %
                           (ih.nbpp, ih.pvtype))
    
def _set_dtype(ih, data_type):
    '''The data_type should be a numpy type. Note that the NITF image is 
    always big endian (the opposite of the intel ordering). Since the 
    various read/
    write classes handle the endian conversion, we don't worry here if the
    data_type is big or little endian, so np.dtype('<i2'), np.dtype('i2') and
    np.dtype('>i2') are all treated the same by this function.
    
    Note this results in the weird behavior that blah.dtype = d_type and
    then blah.dtype == d_type might return false (if we converted to big
    endian). I believe this is what we want, but if it turns out that this
    is confusing or a bad idea, then we can revisit this.
    '''
    if (data_type == np.uint8):
        ih.abpp = 8
        ih.nbpp = 8
        ih.pvtype = "INT"
    elif (data_type == np.int8):
        ih.abpp = 8
        ih.nbpp = 8
        ih.pvtype = "SI"
    elif (data_type == np.dtype('<u2') or data_type == np.dtype('>u2')):
        ih.abpp = 16
        ih.nbpp = 16
        ih.pvtype = "INT"
    elif (data_type == np.dtype('<i2') or data_type == np.dtype('>i2')):
        ih.abpp = 16
        ih.nbpp = 16
        ih.pvtype = "SI"
    elif (data_type == np.dtype('<u4') or data_type == np.dtype('>u4')):
        ih.abpp = 32
        ih.nbpp = 32
        ih.pvtype = "INT"
    elif (data_type == np.dtype('<i4') or data_type == np.dtype('>i4')):
        ih.abpp = 32
        ih.nbpp = 32
        ih.pvtype = "SI"
    elif (data_type == np.dtype('<f4') or data_type == np.dtype('>f4')):
        ih.abpp = 32
        ih.nbpp = 32
        ih.pvtype = "R"
    elif (data_type == np.dtype('<c8') or data_type == np.dtype('>c8')):
        ih.abpp = 64
        ih.nbpp = 64
        ih.pvtype = "C"
    elif (data_type == np.dtype('<f8') or data_type == np.dtype('>f8')):
        ih.abpp = 64
        ih.nbpp = 64
        ih.pvtype = "R"
    elif (data_type == np.dtype('<c16') or data_type == np.dtype('>c16')):
        ih.abpp = 128
        ih.nbpp = 128
        ih.pvtype = "C"
    else:
        raise RuntimeError("Unsupported data_type")

NitfImageSubheader.dtype = property(_dtype, _set_dtype)

def _shape(self):
    return (self.number_band, self.nrows, self.ncols)

NitfImageSubheader.shape = property(_shape)

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

def _get_security(self):
    return NitfSecurity.get_security(self, "i")

def _set_security(self, s):
    s.set_security(self, "i")

NitfImageSubheader.security = property(_get_security, _set_security)

__all__ = ["NitfImageSubheader", "set_default_image_subheader"]
