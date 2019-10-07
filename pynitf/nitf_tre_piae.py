from .nitf_tre import *

hlp = '''This is the PIAIMC TRE, Profile for Imagery Access Image

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002 V4.0, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

PIAIMC is documented at C-8.
'''
desc = ["PIAIMC",
        ["cloudcvr", "Cloud Cover", 3, int, {"optional" : True}],
        ["srp", "Standard Radiometric Product", 1, str, {"optional" : True}],
        ["sensormode", "Sensor Mode", 12, str, {"optional" : True}],
        ["sensname", "Sensor Name", 18, str, {"optional" : True}],
        ["source", "Source", 255, str, {"optional" : True}],
        ["comgen", "Compression Generation", 2, int, {"optional" : True, 'optional_char' : '-'}],
        ["subqual", "Subjective Quality", 1, str, {"optional" : True}],
        ["piamsnnum", "PIA Mission Number", 7, str, {"optional" : True}],
        ["camspecs", "Camera Specs", 32, str, {"optional" : True}],
        ["projid", "Project ID Code", 2, str, {"optional" : True}],
        ["generation", "Generation", 1, int, {"optional" : True, 'optional_char' : '-'}],
        ["esd", "Exploitation Support Data", 1, str, {"optional" : True}],
        ["othercond", "Other Conditions", 2, str, {"optional" : True}],
        ["mean_gsd", "Mean GSD", 7, float, {"frmt" : "%07.1lf", "optional": True}],
        ["idatum", "Image Datum", 3, str, {"optional" : True}],
        ["iellip", "Image Ellipsoid", 3, str, {"optional" : True}],
        ["preproc", "Image Processing Level", 2, str, {"optional" : True}],
        ["iproj", "Image Projection System", 2, str, {"optional" : True}],
        ["sattrack", "Satellite Track", 8, int, {"optional" : True}],
        ]

TrePIAIMC = create_nitf_tre_structure("TrePIAIMC", desc, hlp=hlp)

__all__ = ["TrePIAIMC" ]
