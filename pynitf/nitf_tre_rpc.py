from .nitf_tre import Tre, tre_tag_to_cls
import copy
import re

def _tre_rpc_coeff_format(v):
    '''Convert to string for RPC coefficient for a TRE'''
    # If too small to represent, replace with zero
    if(abs(v) < 1e-9):
        return '+0.000000E+0'
    # Error if too big
    if(abs(v) >= 1e10):
        raise RuntimeError("Value is to large to represent in a TRE")
    t = "%+010.6lE" % v
    # Replace 2 digit exponent with 1 digit
    t = re.sub(r'E([+-])0', r'E\1', t)
    return t

hlp = '''This is the RPC TRE.

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002 V4.0, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

RPC00B is documented at E-62.
'''
desc = [["success", "Success", 1, int],
        ["err_bias", "Error - Bias", 7, float, {"frmt" : "%07.2lf"}],
        ["err_rand", "Error - Random", 7, float, {"frmt" : "%07.2lf"}],
        ["line_off", "Line Offset", 6, int],
        ["samp_off", "Sample Offset", 5, int],
        ["lat_off", "Geodetic Latitude Offset", 8, float, {"frmt" : "%+08.4lf"}],
        ["long_off", "Geodetic Longitude Offset", 9, float, {"frmt" : "%+09.4lf"}],
        ["height_off", "Geodetic Height Offset", 5, int],
        ["line_scale", "Line Scale", 6, int],
        ["samp_scale", "Sample Scale", 5, int],
        ["lat_scale", "Geodetic Latitude Scale", 8, float, {"frmt" : "%+08.4lf"}],
        ["long_scale", "Geodetic Longitude Scale", 9, float, {"frmt": "%+09.4lf"}],
        ["height_scale", "Geodetic Height Scale", 5, int, {"frmt": "%+05d"}],
        [["loop", "20"],
         ["line_num_coeff", "Line Numerator Coefficient", 12, float, {"frmt": _tre_rpc_coeff_format}]],
        [["loop", "20"],
         ["line_den_coeff", "Line Denominator Coefficient", 12, float, {"frmt": _tre_rpc_coeff_format}]],
        [["loop", "20"],
         ["samp_num_coeff", "Sample Numerator Coefficient", 12, float, {"frmt": _tre_rpc_coeff_format}]],
        [["loop", "20"],
         ["samp_den_coeff", "Sample Denominator Coefficient", 12, float, {"frmt": _tre_rpc_coeff_format}]],
]

class TreRPC00B(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "RPC00B"

tre_tag_to_cls.add_cls(TreRPC00B)    

# RCP00A is the same format at the OOB, we just have the parameters in
# a different order (as already handled by the Rpc class). But this is
# a separate TRE

desc2 = copy.deepcopy(desc)
desc2[0] = "RPC00A"

class TreRPC00A(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "RPC00A"

tre_tag_to_cls.add_cls(TreRPC00A)    

__all__ = [ "TreRPC00B", "TreRPC00A"]
