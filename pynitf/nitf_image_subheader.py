from __future__ import print_function
from .nitf_field import *
import six
import numpy as np

hlp = '''This is a NITF image subheader. The field names can be pretty
cryptic, but these are documented in detail in the NITF 2.10 documentation
(MIL-STD-2500C, available at http://www.gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf).

The NITF image subheader is described in Table A-3, starting page 78.
'''

    
desc = [['im', "", 2, str],
        ['iid1', "", 10, str],
        ['idatim', "", 14, str],
        ['tgtid', "", 17, str],
        ['iid2', "", 80, str],
        ['isclas', "", 1, str, {'default' : 'U'}],
        ['isclsy', "", 2, str],
        ['iscode', "", 11, str],
        ['isctlh', "", 2, str],
        ['isrel', "", 20, str],
        ['isdctp', "", 2, str],
        ['isdcdt', "", 8, str],
        ['isdcxm', "", 4, str],
        ['isdg', "", 1, str],
        ['isdgdt', "", 8, str],
        ['iscltx', "", 43, str],
        ['iscatp', "", 1, str],
        ['iscaut', "", 40, str],
        ['iscrsn', "", 1, str],
        ['issrdt', "", 8, str],
        ['isctln', "", 15, str],
        ['encryp', "", 1, int],
        ['isorce', "", 42, str],
        ['nrows', "", 8, int],
        ['ncols', "", 8, int],
        ['pvtype', "", 3, str, {'default' : 'INT'}],
        ['irep', "", 8, str, {'default' : 'MONO'}],
        ['icat', "", 8, str, {'default' : 'VIS'}],
        ['abpp', "", 2, int, {'default' : 8}],
        ['pjust', "", 1, str, {'default' : 'R'}],
        ['icords', "", 1, str],
        ['igeolo', "", 60, str, {'condition' : "f.icords.rstrip() != ''"}],
        ['nicom', "", 1, int],
        [["loop", "f.nicom"],
         ["icom", "", 80, str]],
        ['ic', "", 2, str, {'default' : 'NC'}],
        ['comrat', "", 4, str, {'condition' : "f.ic not in ('NC', 'NM')"}], 
        ['nbands', "", 1, int, {'default' : 1}],
        ['xbands', "", 5, int, {'condition' : "f.nbands == 0"}],
        [["loop", "f.nbands if f.nbands > 0 else f.xbands"],
         ['irepband', "", 2, str, {'default' : 'M'}],
         ['isubcat', "", 6, str],
         ['ifc', "", 1, str],
         ['imflt', "", 3, str],
         ['nluts', "", 1, int],
         ['nelut', "", 5, int, {'condition' : "f.nluts[i1] != 0"}],
         [["loop", "f.nluts[i1]"],
          ['lutd', "", 'f.nelut[i1]', None, {'field_value_class' : FieldData}]
         ],
        ],
        ['isync', "", 1, int],
        ['imode', "", 1, str, {'default' : 'B'}],
        ['nbpr', "", 4, int, {'default' : 1 }],
        ['nbpc', "", 4, int, {'default' : 1}],
        ['nppbh', "", 4, int],
        ['nppbv', "", 4, int],
        ['nbpp', "", 2, int, {'default' : 8 }],
        ['idlvl', "", 3, int],
        ['ialvl', "", 3, int],
        ['iloc', "", 10, str, {'default' : '0000000000'}],
        ['imag', "", 4, str, {'default' : '1.0'}],
        ['udidl', "", 5, int],
        ['udofl', "", 3, int, {'condition' : 'f.udidl != 0'}],
        ['udid', "", 'f.udidl', None, {'field_value_class' : FieldData,
                                     'size_offset' : 3}],
        ['ixshdl', "", 5, int],
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
            numbands = self.xbands
    print("%d X %d, %d Bands, %d/%d bpp"
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
        return np.uint8
    elif(ih.nbpp == 8 and ih.pvtype == "SI"):
        return np.int8
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
    elif(ih.nbpp ==32 and ih.pvtype == "C"):
        return np.dtype('>c4')
    elif(ih.nbpp ==64 and ih.pvtype == "R"):
        return np.dtype('>f8')
    elif(ih.nbpp ==64 and ih.pvtype == "C"):
        return np.dtype('>c8')
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
    elif (data_type == np.dtype('<c4') or data_type == np.dtype('>c4')):
        ih.abpp = 32
        ih.nbpp = 32
        ih.pvtype = "C"
    elif (data_type == np.dtype('<f8') or data_type == np.dtype('>f8')):
        ih.abpp = 64
        ih.nbpp = 64
        ih.pvtype = "R"
    elif (data_type == np.dtype('<c8') or data_type == np.dtype('>c8')):
        ih.abpp = 64
        ih.nbpp = 64
        ih.pvtype = "C"
    else:
        raise RuntimeError("Unsupported data_type")

NitfImageSubheader.dtype = property(_dtype, _set_dtype)

def set_default_image_subheader(ih, nrow, ncol, data_type, numbands=1,
                                iid1 = "Test data",
                                iid2 = "This is sample data.",
                                idatim = "20160101120000"):
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

    for b in range(numbands):
        ih.irepband[b] = 'M'
        ih.isubcat[b] = b + 1
        ih.nluts[b] = 0

    # If numbands is 1, we end up with the irepband being "R"
    ih.irepband[numbands - 1] = "B"
    ih.irepband[int(numbands / 2)] = "G"
    ih.irepband[0] = "R"

__all__ = ["NitfImageSubheader", "set_default_image_subheader"]
