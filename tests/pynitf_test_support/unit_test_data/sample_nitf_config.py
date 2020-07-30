# Some sample configuration. Used in nitf_diff_test.py

from __main__ import nitf_diff

# Don't care if content of an attached file is different
nitf_diff.config["DesExtDefContent"] = { 'exclude_but_warn' : True }

# If file is different, the header will also be different, so ignore
# that also

nitf_diff.config["DesExtContentHeader"] = {
    'exclude_but_warn' : ['content_headers_len', 'content_headers'],
}

