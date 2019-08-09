from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the ILLUMA TRE, Illumination for Spectral Products. 

The field names can be pretty cryptic, but are documented in detail in 
the NGA's SNIP documentation. It is current in draft and is subject to change.

The SNIP documentation is currently not available to the public.

!!! Note that in the current version of ILLUMA you can choose between using traditional fields and using a single
!!! XML file. The conditional flag in choosing between the two is the value of the CEL field in the TRE subheader.
!!! This practice is highly unorthodox and our current pynitf design doesn't easily support this.
!!! For now we will only support the traditional way of using this TRE. Once this TRE is finalized and ratified
!!! by the NTB, we can implement the final version.
'''

desc = ["ILLUMA",
        ["sol_az", "Sun Azimuth Angle", 5, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
        ["sol_el", "Sun Elevation Angle", 5, float, {'frmt': '%+04.1f', 'optional': True, 'optional_char' : '-'}],
        ["com_sol_il", "Computed Solar Illumination", 5, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
        ["lun_el", "Lunar Elevation Angle", 5, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
        ["lun_ph_ang", "Phase Angle of the Moon in Degrees", 6, float, {'frmt': '%+05.1f', 'optional': True, 'optional_char' : '-'}],
        ["lun_az", "Lunar Azimuth Angle", 5, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
        ["com_lun_il", "Computed Lunar Illumination", 5, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
        ["com_tot_nat_il", "Computed Total Natural Illumination", 5, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
        ["sol_lun_dis_ad", "Solar/Lunar Distance Adjustment", 3, float, {'frmt': '%03.1f', 'optional': True, 'optional_char' : '-'}],
        ["art_ill_min", "Minimum Artificial Illumination", 5, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
        ["art_ill_max", "Maximum Artificial Illumination", 5, float, {'frmt': '%05.1f', 'optional': True, 'optional_char' : '-'}],
]

#TreILLUMA = create_nitf_tre_structure("TreILLUMA",desc,hlp=hlp)

