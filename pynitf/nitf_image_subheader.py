from __future__ import print_function
from .nitf_field import *

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
        ['imode', "", 1, str, {'default' : 'S'}],
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
