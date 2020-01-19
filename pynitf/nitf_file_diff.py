from .nitf_file import NitfFile
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
import copy

class NitfDiff(object):
    '''Class that handles the overall NITF diff between two files.'''
    def __init__(self):
        self.config = copy.copy(NitfDiffHandleSet.default_config)
        self.handle_set = copy.copy(NitfDiffHandleSet.default_handle_set())

    def _update_dict(self, d, u):
        '''Recursively update a dictionary with a second dictionary. Handles
        nested dict.'''
        for k, v in u.items():
            if isinstance(v, collections.abc.Mapping):
                d[k] = self.update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def update_config(self, u):
        '''Update the config dict with an update dictionary. Handles
        nested dictionaries.'''
        self.config = self._update_dict(self.config, u)
        
    def compare(self, file1, file2):
        f1 = NitfFile(file1)
        f2 = NitfFile(file2)
        return self.compare_obj(f1, f2)

    def compare_obj(self, obj1, obj2):
        '''Convenience short hand for calling self.handle_set.handle because
        we do that a lot. This can also be useful to compare
        individual components of a NITF file (e.g, you have 2 files
        open and want to know if two NitfImageSegment are the same)
        '''
        return self.handle_set.handle(obj1, obj2, self)


class NitfFileHandle(NitfDiffHandle):
    '''Compare two files. This particular class doesn't try to do anything
    clever about reordering, so it compares the first image segment in file
    1 with the first image segment in file 2 etc.'''
    def handle_diff(self, f1, f2, nitf_diff):
        if(not isinstance(f1, NitfFile) or
           not isinstance(f2, NitfFile)):
            return (False, None)
        is_same = True
        is_same = (nitf_diff.compare_obj(f1.file_header, f2.file_header)
                   and is_same)
        for (desc, lis1, lis2) in \
            [("file level TREs", f1.tre_list, f2.tre_list),
             ("image segments", f1.image_segment, f2.image_segment),
             ("graphic segments", f1.graphic_segment, f2.graphic_segment),
             ("text segments", f1.text_segment, f2.text_segment),
             ("des segments", f1.des_segment, f2.des_segment),
             ("res segments", f1.res_segment, f2.res_segment),
             ]:
            if(len(lis1) != len(lis2)):
                logger = logging.getLogger('nitf_diff')
                logger.difference("File 1 has %d %s while file 2 has %d" %
                                  (len(lis1), desc, len(lis2)))
                is_same = False
            for i in range(min(len(lis1), len(lis2))):
                is_same = nitf_diff.compare_obj(lis1[i], lis2[i]) and is_same
        return (True, is_same)

NitfDiffHandleSet.add_default_handle(NitfFileHandle())

__all__ = ["NitfDiff", "NitfFileHandle",]
