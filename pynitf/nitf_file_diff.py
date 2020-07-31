from .nitf_file import (NitfFile, NitfImageSegment, NitfGraphicSegment,
                        NitfTextSegment, NitfDesSegment, NitfResSegment)
from .nitf_diff_handle import (NitfDiffHandle, NitfDiffHandleSet,
                               DiffContextFilter)
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


class ImageSegmentDiff(NitfDiffHandle):
    '''Compare two image segments.'''
    def handle_diff(self, iseg1, iseg2, nitf_diff):
        if(not isinstance(iseg1, NitfImageSegment) or
           not isinstance(iseg2, NitfImageSegment)):
            return (False, None)
        with nitf_diff.diff_context("ImageSegment '%s'" % iseg1.iid1):
            is_same = nitf_diff.compare_obj(iseg1.subheader, iseg2.subheader)
            t1 = [i for i in iseg1.tre_list if not nitf_diff.skip_obj(i)]
            t2 = [i for i in iseg2.tre_list if not nitf_diff.skip_obj(i)]
            if(len(t1) != len(t2)):
                logger.difference("Segment 1 has %d TREs while Segment 2 has %d",
                                  len(t1), len(t2))
                is_same = False
            for i in range(min(len(t1), len(t2))):
                is_same = nitf_diff.compare_obj(t1[i],
                                                t2[i]) and is_same
            is_same = nitf_diff.compare_obj(iseg1.data, iseg2.data) and is_same
            return (True, is_same)

NitfDiffHandleSet.add_default_handle(ImageSegmentDiff())
                           
class GraphicSegmentDiff(NitfDiffHandle):
    '''Compare two graphics segments.'''
    def handle_diff(self, gseg1, gseg2, nitf_diff):
        if(not isinstance(gseg1, NitfGraphicSegment) or
           not isinstance(gseg2, NitfGraphicSegment)):
            return (False, None)
        with nitf_diff.diff_context("GraphicSegment '%s'" % gseg1.subheader.sid):
            is_same = nitf_diff.compare_obj(gseg1.subheader, gseg2.subheader)
            t1 = [i for i in gseg1.tre_list if not nitf_diff.skip_obj(i)]
            t2 = [i for i in gseg2.tre_list if not nitf_diff.skip_obj(i)]
            if(len(t1) != len(t2)):
                logger.difference("Segment 1 has %d TREs while Segment 2 has %d",
                                  len(t1), len(t2))
                is_same = False
            for i in range(min(len(t1), len(t2))):
                is_same = nitf_diff.compare_obj(t1[i],
                                                t2[i]) and is_same
            is_same = nitf_diff.compare_obj(gseg1.data, gseg2.data) and is_same
            return (True, is_same)

NitfDiffHandleSet.add_default_handle(GraphicSegmentDiff())

class TextSegmentDiff(NitfDiffHandle):
    '''Compare two text segments.'''
    def handle_diff(self, tseg1, tseg2, nitf_diff):
        if(not isinstance(tseg1, NitfTextSegment) or
           not isinstance(tseg2, NitfTextSegment)):
            return (False, None)
        with nitf_diff.diff_context("TextSegment '%s'" % tseg1.subheader.textid):
            is_same = nitf_diff.compare_obj(tseg1.subheader, tseg2.subheader)
            t1 = [i for i in tseg1.tre_list if not nitf_diff.skip_obj(i)]
            t2 = [i for i in tseg2.tre_list if not nitf_diff.skip_obj(i)]
            if(len(t1) != len(t2)):
                logger.difference("Segment 1 has %d TREs while Segment 2 has %d",
                                  len(t1), len(t2))
                is_same = False
            for i in range(min(len(t1), len(t2))):
                is_same = nitf_diff.compare_obj(t1[i],
                                                t2[i]) and is_same
            is_same = nitf_diff.compare_obj(tseg1.data, tseg2.data) and is_same
            return (True, is_same)

NitfDiffHandleSet.add_default_handle(TextSegmentDiff())

class DesSegmentDiff(NitfDiffHandle):
    '''Compare two DES segments.'''
    def handle_diff(self, dseg1, dseg2, nitf_diff):
        if(not isinstance(dseg1, NitfDesSegment) or
           not isinstance(dseg2, NitfDesSegment)):
            return (False, None)
        if(dseg1.subheader.desid == "TRE_OVERFLOW" and
           dseg2.subheader.desid == "TRE_OVERFLOW"):
            # Skip checking this DES, we already check this when
            # we compare TREs
            return (True, True)
        with nitf_diff.diff_context("DES"):
            is_same = nitf_diff.compare_obj(dseg1.subheader,
                                            dseg2.subheader)
            if(dseg1.des.user_subheader):
                is_same = nitf_diff.compare_obj(dseg1.des.user_subheader,
                                       dseg2.des.user_subheader) and is_same
            is_same = nitf_diff.compare_obj(dseg1.des, dseg2.des) and is_same
            return (True, is_same)

NitfDiffHandleSet.add_default_handle(DesSegmentDiff())

class ResSegmentDiff(NitfDiffHandle):
    '''Compare two Reserved segments.'''
    def handle_diff(self, rseg1, rseg2, nitf_diff):
        if(not isinstance(rseg1, NitfResSegment) or
           not isinstance(rseg2, NitfResSegment)):
            return (False, None)
        with nitf_diff.diff_context("ResSegment '%s'" % rseg1.subheader.resid):
            is_same = nitf_diff.compare_obj(rseg1.subheader, rseg2.subheader)
            if(rseg1.des.user_subheader):
                is_same = nitf_diff.compare_obj(rseg1.des.user_subheader,
                                       rseg2.des.user_subheader) and is_same
            is_same = nitf_diff.compare_obj(rseg1.data, rseg2.data) and is_same
            return (True, is_same)

NitfDiffHandleSet.add_default_handle(ResSegmentDiff())

__all__ = ["NitfDiff", "NitfFileHandle", "ImageSegmentDiff",
           "GraphicSegmentDiff", "TextSegmentDiff", "DesSegmentDiff",
           "ResSegmentDiff"]

