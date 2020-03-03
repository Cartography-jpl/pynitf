from .nitf_tre import Tre, tre_tag_to_cls

hlp = '''This is the RSMIDA TRE, Replacement Sensor Model Identification. 

The field names can be pretty cryptic, but are documented in detail in 
the NITF TRE documentation (STDI-0002 V4.0, available at 
http://www.gwg.nga.mil/ntb/baseline/docs/stdi0002).

There is a table in the main body on page vii that gives the a pointer for 
where in the document a particular TRE is defined.

RSMIDA is documented at U-6, which points to other documentation, such as
"Replacement Sensor Model Tagged Record Extensions Specification for NITF
2.1" (http://www.gwg.nga.mil/ntb/baseline/docs/RSM/RSM_NITF_TREs_v1.0_.pdf)
'''

_second_format = "%09.6lf"
_trg_format = "%21.14E"

desc = [["iid", "Image Identifier", 80, str],
        ["edition", "RSM Image Support Data Edition", 40, str],
        ["isid", "Image Sequence Identifier", 40, str],
        ["sid", "Sensor Identifier", 40, str],
        ["stid", "Sensor Type Identifier", 40, str],
        ["year", "Year of Image Acquisition", 4, int, {'optional':True}],
        ["month", "Month of Image Acquisition", 2, int, {'optional':True}],
        ["day", "Day of Image Acquisition", 2, int, {'optional':True}],
        ["hour", "Hour of Image Acquisition", 2, int, {'optional':True}],
        ["minute", "Minute of Image Acquisition", 2, int, {'optional':True}],
        ["second", "Second of Image Acquisition", 9, float, {'optional':True, 'frmt' : _second_format}],
        ["nrg", "Number of Rows Acquired Simultaneously", 8, int, {'optional':True}],
        ["ncg", "Number of Columns Acquired Simultaneously", 8, int, {'optional':True}],
        ["trg", "Time Between Adjacent Row Groups", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["tcg", "Time Between Adjacent Column Groups", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["grndd", "Ground Domain Form", 1, str],
        ["xuor", "Regular Coordinate Origin (XUOR)", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["yuor", "Regular Coordinate Origin (YUOR)", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["zuor", "Regular Coordinate Origin (ZUOR)", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["xuxr", "Rectangular Coord Unit Vector (XUXR)", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["xuyr", "Rectangular Coord Unit Vector (XUYR)", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["xuzr", "Rectangular Coord Unit Vector (XUZR)", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["yuxr", "Rectangular Coord Unit Vector (YUXR)", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["yuyr", "Rectangular Coord Unit Vector (YUYR)", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["yuzr", "Rectangular Coord Unit Vector (YUZR)", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["zuxr", "Rectangular Coord Unit Vector (ZUXR)", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["zuyr", "Rectangular Coord Unit Vector (ZUYR)", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["zuzr", "Rectangular Coord Unit Vector (ZUZR)", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["v1x", "Vertex 1 - X coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v1y", "Vertex 1 - Y coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v1z", "Vertex 1 - Z coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v2x", "Vertex 2 - X coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v2y", "Vertex 2 - Y coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v2z", "Vertex 2 - Z coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v3x", "Vertex 3 - X coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v3y", "Vertex 3 - Y coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v3z", "Vertex 3 - Z coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v4x", "Vertex 4 - X coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v4y", "Vertex 4 - Y coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v4z", "Vertex 4 - Z coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v5x", "Vertex 5 - X coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v5y", "Vertex 5 - Y coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v5z", "Vertex 5 - Z coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v6x", "Vertex 6 - X coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v6y", "Vertex 6 - Y coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v6z", "Vertex 6 - Z coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v7x", "Vertex 7 - X coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v7y", "Vertex 7 - Y coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v7z", "Vertex 7 - Z coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v8x", "Vertex 8 - X coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v8y", "Vertex 8 - Y coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["v8z", "Vertex 8 - Z coord of the RSM ground domain", 21, float, {'frmt' : _trg_format}],
        ["grpx", "Ground Reference Point X", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["grpy", "Ground Reference Point Y", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["grpz", "Ground Reference Point Z", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["fullr", "Number of Rows in Full Image", 8, int, {'optional':True}],
        ["fullc", "Number of Cols in Full Image", 8, int, {'optional':True}],
        ["minr", "Minimum Row", 8, int],
        ["maxr", "Maximum Row", 8, int],
        ["minc", "Minimum Col", 8, int],
        ["maxc", "Maximum Col", 8, int],
        ["ie0", "Illum Elevation Angle Const Coeff", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["ier", "Illum Elevation Angle Coeff Per Row", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["iec", "Illum Elevation Angle Coeff Per Col", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["ierr", "Illum Elevation Angle Coeff Per Row^2", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["ierc", "Illum Elevation Angle Coeff Per Row-Col", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["iecc", "Illum Elevation Angle Coeff Per Col^2", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["ia0", "Illum Azimuth Angle Const", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["iar", "Illum Azimuth Angle Coeff Per Row", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["iac", "Illum Azimuth Angle Coeff Per Col", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["iarr", "Illum Azimuth Angle Coeff Per Row^2", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["iarc", "Illum Azimuth Angle Coeff Per Row-Col", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["iacc", "Illum Azimuth Angle Coeff Per Col^2", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["spx", "Sensor x-position", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["svx", "Sensor x-velocity", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["sax", "Sensor x-acceleration", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["spy", "Sensor y-position", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["svy", "Sensor y-velocity", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["say", "Sensor y-acceleration", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["spz", "Sensor z-position", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["svz", "Sensor z-velocity", 21, float, {'optional':True, 'frmt' : _trg_format}],
        ["saz", "Sensor z-acceleration", 21, float, {'optional':True, 'frmt' : _trg_format}],
]

class TreRSMIDA(Tre):
    __doc__ = hlp
    desc = desc
    tre_tag = "RSMIDA"

tre_tag_to_cls.add_cls(TreRSMIDA)    

__all__ = [ "TreRSMIDA" ]
