from .nitf_segment_data_handle import (NitfText,
                                       NitfSegmentDataHandleSet)
from .nitf_diff_handle import (NitfDiffHandle, NitfDiffHandleSet,
                               DiffContextFilter)
import io
import logging

logger = logging.getLogger('nitf_diff')

class NitfTextStr(NitfText):
    '''Implementation that just treats the text data as string.'''

    def __init__(self, string=None, seg=None):
        super().__init__(seg)
        self.string = string
        
    def __str__(self):
        return "NitfTextStr:\n%s" % (self.string_as_str)

    @property
    def string_as_str(self):
        '''Present the data as a str object, even if it happen to
        be bytes'''
        if isinstance(self.string, str):
            return self.string
        return self.string.decode('utf-8')

    @property
    def string_as_bytes(self):
        '''Present the data as a str object, even if it happen to
        be bytes'''
        if isinstance(self.string, str):
            return self.string.encode('utf-8')
        return self.string
    
    def read_from_file(self, fh, seg_index=None):
        self.string = fh.read(self._seg().data_size)
        return True

    def __getstate__(self):
        return {"string" : self.string_as_str }

    def __setstate__(self, d):
        self.string = d["string"]

    def write_to_file(self, fh):
        fh.write(self.string_as_bytes)

class TextStrDiff(NitfDiffHandle):
    '''Compare two NitfTextStr'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("TextStr", {})
    
    def handle_diff(self, g1, g2, nitf_diff):
        with nitf_diff.diff_context("TextStr", add_text=True):
            if(not isinstance(g1, NitfTextStr) or
               not isinstance(g2, NitfTextStr)):
                return (False, None)
            is_same = g1.string_as_str == g2.string_as_str
            if(not is_same):
                logger.difference("Text data is not the same")
            return (True, is_same)

NitfDiffHandleSet.add_default_handle(TextStrDiff())
NitfSegmentDataHandleSet.add_default_handle(NitfTextStr)

__all__ = ["NitfTextStr", ]
