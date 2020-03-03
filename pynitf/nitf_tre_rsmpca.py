from .nitf_tre import Tre, tre_tag_to_cls

hlp = '''This is the RSMPCA TRE, the Replacement Senor Model Polynomial
Coefficients version A. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002 V4.0, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

RSMPCA is documented at U-6, which points to other documentation, such as
"Replacement Sensor Model Tagged Record Extensions Specification for NITF
2.1" (http://www.gwg.nga.mil/ntb/baseline/docs/RSM/RSM_NITF_TREs_v1.0_.pdf)
'''
_rfep_format = "%+21.14E"

desc = [["iid", "Image Identifier", 80, str, {'optional':True}],
        ["edition", "RSM Image Support Data Edition", 40, str],
        ["rsn", "Row Section Number", 3, int],
        ["csn", "Column Section Number", 3, int],
        ["rfep", "Row Fitting Error", 21, float,
         {'frmt' : _rfep_format, 'optional' : True}],
        ["cfep", "Col Fitting Error", 21, float,
         {'frmt' : _rfep_format, 'optional' : True}],
        ["rnrmo", "Row Normalization Offset", 21, float,
         {'frmt' : _rfep_format}],
        ["cnrmo", "Col Normalization Offset", 21, float,
         {'frmt' : _rfep_format}],
        ["xnrmo", "X Normalization Offset", 21, float,
         {'frmt' : _rfep_format}],
        ["ynrmo", "Y Normalization Offset", 21, float,
         {'frmt' : _rfep_format}],
        ["znrmo", "Z Normalization Offset", 21, float,
         {'frmt' : _rfep_format}],
        ["rnrmsf", "Row Normalization Scale Factor", 21, float,
         {'frmt' : _rfep_format}],
        ["cnrmsf", "Col Normalization Scale Factor", 21, float,
         {'frmt' : _rfep_format}],
        ["xnrmsf", "X Normalization Scale Factor", 21, float,
         {'frmt' : _rfep_format}],
        ["ynrmsf", "Y Normalization Scale Factor", 21, float,
         {'frmt' : _rfep_format}],
        ["znrmsf", "Z Normalization Scale Factor", 21, float,
         {'frmt' : _rfep_format}],
        ["rnpwrx", "Row Numerator Poly Max Power of X", 1, int],
        ["rnpwry", "Row Numerator Poly Max Power of Y", 1, int],
        ["rnpwrz", "Row Numerator Poly Max Power of Z", 1, int],
        ["rntrms", "Row Numerator Poly Number of Poly Terms", 3, int],
        [["loop", "f.rntrms"],
        ["rnpcf", "Poly Coeff", 21, float, {'frmt' : _rfep_format}],
        ],
        ["rdpwrx", "Row Denominator Poly Max Power of X", 1, int],
        ["rdpwry", "Row Denominator Poly Max Power of Y", 1, int],
        ["rdpwrz", "Row Denominator Poly Max Power of Z", 1, int],
        ["rdtrms", "Row Denominator Poly Number of Poly Terms", 3, int],
        [["loop", "f.rdtrms"],
        ["rdpcf", "Poly Coeff", 21, float, {'frmt' : _rfep_format}],
        ],
        ["cnpwrx", "Row Numerator Poly Max Power of X", 1, int],
        ["cnpwry", "Row Numerator Poly Max Power of Y", 1, int],
        ["cnpwrz", "Row Numerator Poly Max Power of Z", 1, int],
        ["cntrms", "Row Numerator Poly Number of Poly Terms", 3, int],
        [["loop", "f.cntrms"],
        ["cnpcf", "Poly Coeff", 21, float, {'frmt' : _rfep_format}],
        ],
        ["cdpwrx", "Row Denominator Poly Max Power of X", 1, int],
        ["cdpwry", "Row Denominator Poly Max Power of Y", 1, int],
        ["cdpwrz", "Row Denominator Poly Max Power of Z", 1, int],
        ["cdtrms", "Row Denominator Poly Number of Poly Terms", 3, int],
        [["loop", "f.cdtrms"],
        ["cdpcf", "Poly Coeff", 21, float, {'frmt' : _rfep_format}],
        ],
]

class TreRSMPCA(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "RSMPCA"

    @property
    def row_section_number(self):
        return self.rsn

    @property
    def col_section_number(self):
        return self.csn
    
tre_tag_to_cls.add_cls(TreRSMPCA)    

__all__ = [ "TreRSMPCA" ]
