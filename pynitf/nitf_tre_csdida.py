from __future__ import print_function
from .nitf_field import *
from .nitf_tre import *
import six

hlp = '''This is the CSDIDA TRE. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0006 V2.1, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0006/NCDRD_18February2010.pdf).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.
'''

desc = ["CSDIDA",
        ["day", "Day of Dataset Collection", 2, int],
        ["month", "Month of Dataset Collection", 3, str],
        ["year", "Year of Dataset Collection", 4, int],
        ["platform_code", "Platform Identification", 2, str],
        ["vehicle_id", "Vehicle Number", 2, int],
        ["pass_", "Pass Number", 2, int],
        ["operation", "Operation Number", 3, int],
        ["sensor_id", "Sensor ID", 2, str],
        ["product_id", "Product ID", 2, str],
        ["reserved_1", "Fill", 4, str, {'default' : '0000'}],
        ["time", "Image Start Time", 14, int],
        ["process_time", "Process Completion Time", 14, int],
        ["reserved_2", "Fill", 2, int, {'default' : 0}],
        ["reserved_3", "Fill", 2, int, {'default' : 1}],
        ["reserved_4", "Fill", 1, str, {'default' : 'N'}],
        ["reserved_5", "Fill", 1, str, {'default' : 'N'}],
        ["software_version_number", "Software version used", 10, str],
]

TreCSDIDA = create_nitf_tre_structure("TreCSDIDA",desc,hlp=hlp)

__all__ = [ "TreCSDIDA" ]
