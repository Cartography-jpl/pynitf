from .nitf_file import (NitfFile, NitfSegment)
from .nitf_diff_handle import (NitfDiffHandle, NitfDiffHandleSet,
                               DiffContextFilter)
from .nitf_file_merge import NitfFileMerge
from .nitf_file_json import NitfFileJson
import copy
import logging
from contextlib import contextmanager

logger = logging.getLogger('nitf_diff')

class NitfDiff(object):
    '''Class that handles the overall NITF diff between two files.

    Much of the configuration is tied to the various difference handles,
    but overall configuration:
       skip_obj_func - A possibly empty list of functions. Each object is
           passed to the function before we compare. If any of the functions
           return True, the object is just ignored. This allows us to
           exclude things we don't want to look at in a file.
    '''
    def __init__(self):
        self.config = copy.deepcopy(NitfDiffHandleSet.default_config)
        self.handle_set = copy.deepcopy(NitfDiffHandleSet.default_handle_set())
        self.context_filter = DiffContextFilter("File level")

    def skip_obj(self, obj):
        '''Return True if we should skip this object'''
        flist = self.config.get('skip_obj_func', [])
        for f in flist:
            if(f(obj)):
                return True
        return False

    @contextmanager
    def diff_context(self, v, add_text = False):
        '''"with" context manager for setting the context where we are
        reporting differences. Handles setting the difference context, 
        and then changing back after we leave the block.

        If add_text is set to True, add the context to the existing context.
        This is useful for nested context (e.g. TRE in an image segment)'''
        org_ctx = self.context_filter.ctx
        try:
            if(add_text):
                self.context_filter.ctx += " " + v
            else:
                self.context_filter.ctx = v
            yield
        finally:
            self.context_filter.ctx = org_ctx

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
        
    def compare(self, file1, file2, json_delta=None):
        f1 = NitfFile(file1)
        f2 = NitfFile(file2)
        if(json_delta):
            f2 = NitfFileMerge([NitfFileJson(json_delta), f2])
        return self.compare_obj(f1, f2)
    

    def compare_obj(self, obj1, obj2):
        '''Convenience short hand for calling self.handle_set.handle because
        we do that a lot. This can also be useful to compare
        individual components of a NITF file (e.g, you have 2 files
        open and want to know if two NitfImageSegment are the same)
        '''
        f = self.context_filter if self.context_filter not in logger.filters else None
        try:
            if(f):
                logger.addFilter(f)
            return self.handle_set.handle(obj1, obj2, self)
        finally:
            logger.removeFilter(f)


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
            [("file level TREs",
              [i for i in f1.tre_list if not nitf_diff.skip_obj(i)],
              [i for i in f2.tre_list if not nitf_diff.skip_obj(i)]),

             ("image segments",
              [i for i in f1.image_segment if not nitf_diff.skip_obj(i)],
              [i for i in f2.image_segment if not nitf_diff.skip_obj(i)]),

             ("graphic segments",
              [i for i in f1.graphic_segment if not nitf_diff.skip_obj(i)],
              [i for i in f2.graphic_segment if not nitf_diff.skip_obj(i)]),

             ("text segments",
              [i for i in f1.text_segment if not nitf_diff.skip_obj(i)],
              [i for i in f2.text_segment if not nitf_diff.skip_obj(i)]),

             ("des segments",
              [i for i in f1.des_segment if not nitf_diff.skip_obj(i)],
              [i for i in f2.des_segment if not nitf_diff.skip_obj(i)]),

             ("res segments", 
              [i for i in f1.res_segment if not nitf_diff.skip_obj(i)],
              [i for i in f2.res_segment if not nitf_diff.skip_obj(i)]),
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

class SegmentDiff(NitfDiffHandle):
    '''Compare two NITF segments.'''
    def handle_diff(self, seg1, seg2, nitf_diff):
        if(not isinstance(seg1, NitfSegment) or
           not isinstance(seg2, NitfSegment)):
            return (False, None)
        if(seg1.segment_type() != seg2.segment_type()):
            return (False, None)
        if(seg1.subheader and hasattr(seg1.subheader, "desid") and
           seg1.subheader.desid == "TRE_OVERFLOW" and
           seg2.subheader and hasattr(seg2.subheader, "desid") and           
           seg2.subheader.desid == "TRE_OVERFLOW"):
            # Skip checking this DES, we already check this when
            # we compare TREs
            return (True, True)
        with nitf_diff.diff_context(seg1.short_desc()):
            is_same = nitf_diff.compare_obj(seg1.subheader, seg2.subheader)
            if(seg1.user_subheader):
                is_same = nitf_diff.compare_obj(seg1.user_subheader,
                                                seg2.user_subheader) and is_same
            t1 = [i for i in seg1.tre_list if not nitf_diff.skip_obj(i)]
            t2 = [i for i in seg2.tre_list if not nitf_diff.skip_obj(i)]
            if(len(t1) != len(t2)):
                logger.difference("Segment 1 has %d TREs while Segment 2 has %d",
                                  len(t1), len(t2))
                is_same = False
            for i in range(min(len(t1), len(t2))):
                is_same = nitf_diff.compare_obj(t1[i],
                                                t2[i]) and is_same
            is_same = nitf_diff.compare_obj(seg1.data, seg2.data) and is_same
            return (True, is_same)

NitfDiffHandleSet.add_default_handle(SegmentDiff())

__all__ = ["NitfDiff", "NitfFileHandle", "SegmentDiff"]

