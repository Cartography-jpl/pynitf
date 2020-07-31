# Some sample configuration. Used in nitf_diff_test.py

from __main__ import nitf_diff
import logging
import pynitf

# Don't care if content of an attached file is different
nitf_diff.config["DesExtDefContent"] = { 'exclude_but_warn' : True }

# If file is different, the header will also be different, so ignore
# that also

nitf_diff.config["DesExtContentHeader"] = {
    'exclude_but_warn' : ['content_headers_len', 'content_headers'],
}

nitf_diff.config["TRE"]["USE00A"] = {
    'exclude_but_warn' : ['angle_to_north'],
}

# Pretend that STDIC was a new TRE added and we want to compare to old
# expected data. Just skip STDIC

logger = logging.getLogger('nitf_diff')

def skip_tre(tre_tag):
    def skip_it(obj):
        if(not isinstance(obj, pynitf.Tre) or
           obj.tre_tag != tre_tag):
            return False
        logger.info("Skipping the TRE %s" % tre_tag)
        return True
    return skip_it

nitf_diff.config["skip_obj_func"].append(skip_tre("STDIDC"))
