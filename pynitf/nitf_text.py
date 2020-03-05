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
        if isinstance(self.string, str):
            return "NitfTextStr:\n%s" % (self.string)
        else:
            return "NitfTextStr:\n%s" % (self.string.decode("utf-8"))
        
    def read_from_file(self, fh, seg_index=None):
        self.string = fh.read(self._seg().data_size)
        return True

    def write_to_file(self, fh):
        if isinstance(self.string, str):
            fh.write(self.string.encode('utf-8'))
        else:
            fh.write(self.string)

class TextStrDiff(NitfDiffHandle):
    '''Compare two NitfTextStr'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("TextStr", {})
    
    def handle_diff(self, g1, g2, nitf_diff):
        with nitf_diff.diff_context("TextStr"):
            if(not isinstance(g1, NitfTextStr) or
               not isinstance(g2, NitfTextStr)):
                return (False, None)
            return (True, g1.string == g2.string)

NitfDiffHandleSet.add_default_handle(TextStrDiff())
NitfSegmentDataHandleSet.add_default_handle(NitfTextStr)

__all__ = ["NitfTextStr", ]
