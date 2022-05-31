from .nitf_file import NitfFile

from .nitf_file import NitfFile
from .nitf_tre import add_find_tre_function
from .nitf_tre_engrda import add_engrda_function

class NitfFileMerge(NitfFile):
    '''This is used to merge two NitfFile.

    The specific use case this was designed for was supporting large
    "golden" files for testing with nitf_diff. A common scenario
    during development is to have a few changes to a TRE format or
    something like that. Without something like NitfFileMerge, this
    requires updating the full golden file. With NitfFileMerge you
    can have a small "delta" file with changes to a larger file.

    I'm not 100% sure about the design we want for this. Initially, we'll
    just return the first file that has an entry.'''
    def __init__(self, file_list = []):
        self.file_list = file_list

    @property
    def file_header(self):
        for f in self.file_list:
            if(f.file_header):
                return f.file_header
        return None

    @property
    def image_segment(self):
        for f in self.file_list:
            if(f.image_segment):
                return f.image_segment
        return []

    @property
    def graphic_segment(self):
        for f in self.file_list:
            if(f.graphic_segment):
                return f.graphic_segment
        return []

    @property
    def text_segment(self):
        for f in self.file_list:
            if(f.text_segment):
                return f.text_segment
        return []
    
    @property
    def des_segment(self):
        for f in self.file_list:
            if(f.des_segment):
                return f.des_segment
        return []
    
    @property
    def res_segment(self):
        for f in self.file_list:
            if(f.res_segment):
                return f.res_segment
        return []
    
    @property
    def tre_list(self):
        for f in self.file_list:
            if(f.tre_list):
                return f.tre_list
        return []
    
    def read(self, file_name):
        raise RuntimeError("Can't call read on a NitfFileMerge")

    def write(self, file_name):
        raise RuntimeError("Can't call write on a NitfFileMerge")

__all__ = ["NitfFileMerge", ]
    
