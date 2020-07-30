# Some sample configuration. Used in nitf_diff_test.py

from __main__ import nitf_diff

# Don't care if content of an attached file is different
nitf_diff.config["DesExtDefContent"] = { 'exclude_but_warn' : True }

# If file is different, the header will also be different, so ignore
# that also

nitf_diff.config["DesExtContentHeader"] = {
    'exclude_but_warn' : ['content_headers_len', 'content_headers'],
}

def compare_fixed_value(v):
    def f(a, b):
        return a == v
    return f

nitf_diff.config["TRE"]["USE00A"] = {
    'exclude_but_warn' : ['angle_to_north'],
    'eq_fun' : { 'rev_num' : compare_fixed_value(3200) }
}
