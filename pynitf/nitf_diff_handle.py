from .priority_handle_set import PriorityHandleSet
import logging

logger = logging.getLogger('nitf_diff')

# Add three new logging level to capture diff, diff_but_ignored and
# diff_detailed. We are using
# logging which generally is used to report errors to instead report
# information about differences.
#
# While we could add new level names using logging.addLevelName,
# the python documentation points out
# (https://docs.python.org/3/howto/logging.html#custom-levels) that this
# is a global namespace. We don't want to have any other library that uses
# pynitf forced to use the new level names. So instead, we have a special
# formatter DifferenceFormatter that handles this without adding new names.
#
# Also, if for whatever reason the specific level choosen for the new levels
# causes a problem you can redefine the levels used by changing the value
# of "DIFFERENCE_FOUND", "DIFFERENCE_FOUND_BUT_IGNORED" and "DIFFERENCE_DETAIL"

# ERROR is at 40, WARNING at 30, so the first two are just after ERROR
# in reporting importance.
DIFFERENCE_FOUND = 39
DIFFERENCE_FOUND_BUT_IGNORED = 38
# INFO is at 21, so this is just above it in importance
DIFFERENCE_DETAIL = 21

class DifferenceFormatter(logging.Formatter):
    def __init__(self, add_color = True):
        self.add_color = add_color

    def color_text(self, text, levelno):
        # ANSI colors
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        if(not self.add_color):
            return text
        if(levelno == DIFFERENCE_FOUND):
            return FAIL + text + ENDC
        elif(levelno == DIFFERENCE_FOUND_BUT_IGNORED):
            return OKGREEN + text + ENDC
        elif(levelno == DIFFERENCE_DETAIL):
            return OKBLUE + text + ENDC
        elif(levelno == logging.WARNING):
            return WARNING + text + ENDC
        elif(levelno == logging.ERROR):
            return FAIL + text + ENDC
        return text
    def format(self, record):
        if(hasattr(record, "ctx")):
            ctx = record.ctx + ": "
        else:
            ctx = ""
        if(record.levelno == DIFFERENCE_FOUND):
            return (self.color_text(ctx + "Difference found: ",
                                    DIFFERENCE_FOUND) +
                    record.getMessage())
        if(record.levelno == DIFFERENCE_FOUND_BUT_IGNORED):
            return (self.color_text(ctx + "Difference found, but ignored: ",
                                    DIFFERENCE_FOUND_BUT_IGNORED) +
                    record.getMessage() +
                    " (not considering files different)")
        elif(record.levelno == DIFFERENCE_DETAIL):
            # Less information printed for DIFFERENCE_DETAIL, there will be
            # an overall difference reported.
            return self.color_text("      - " + record.getMessage(),
                                   DIFFERENCE_DETAIL)
        return (self.color_text(record.levelname + ": ", record.levelno) +
                record.getMessage())
        
def _log_difference(msg, *args, **kwargs):
    logger.log(DIFFERENCE_FOUND, msg, *args, **kwargs)
def _log_difference_ignored(msg, *args, **kwargs):
    logger.log(DIFFERENCE_FOUND_BUT_IGNORED, msg, *args, **kwargs)
def _log_difference_detail(msg, *args, **kwargs):
    logger.log(DIFFERENCE_DETAIL, msg, *args, **kwargs)
logger.difference = _log_difference
logger.difference_ignored = _log_difference_ignored
logger.difference_detail = _log_difference_detail

# Handle context information by a filter
class DiffContextFilter(logging.Filter):
    '''Add context information to logging difference.'''
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        
    def filter(self, record):
        record.ctx = self.ctx
        return True

class NitfDiffHandleSet(PriorityHandleSet):
    default_config = {'skip_obj_func' : [] }
    def handle_h(self, h, obj1, obj2, nitf_diff):
        return h.handle_diff(obj1, obj2, nitf_diff)

    

class NitfDiffHandle(object):
    '''Base class for handling difference between two NITF object. Like always,
    you don't need to actually derive from this class if for whatever reason
    this isn't convenient but you should provide this interface.'''
    def handle_diff(self, obj1, obj2, nitf_diff):
        '''Handle determining difference between object. Returns a tuple, with
        the first value indicating if we can handle the types and the second
        indicating if the objects are the same.

        If you have difference to report, you should use the logger
            logger = logging.getLogger('nitf_diff')

        This has had "difference" and "difference_detail" added to
        it for reporting differences, and more detailed information about
        differences (use like you would logger.info).

        So, if we can't handle this particular set of objects, this
        returns (False, None).  Otherwise, it returns (True, True) if
        the objects are the "same" and (True, False) if they are
        different.'''
        raise NotImplementedError()

class AlwaysTrueHandle(NitfDiffHandle):
    '''Handle that always says things are equal. Nice for various test cases
    where we want to check for only a subset of things.'''
    def handle_diff(self, obj1, obj2, nitf_diff):
        logger.info("Using default always match handler")
        logger.info("obj1: %s" % obj1.summary())
        logger.info("obj2: %s" % obj2.summary())
        return (True, True)

__all__ = ["AlwaysTrueHandle", "NitfDiffHandle", "NitfDiffHandleSet",
           "DifferenceFormatter", "DIFFERENCE_DETAIL",
           "DIFFERENCE_FOUND_BUT_IGNORED", "DIFFERENCE_FOUND"]
