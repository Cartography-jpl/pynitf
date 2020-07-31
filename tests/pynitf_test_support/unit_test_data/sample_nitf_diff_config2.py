# Some sample configuration. Used in nitf_diff_test.py

from __main__ import nitf_diff

# Special comparison value
def compare_fixed_value(v):
    def f(a, b):
        return a == v
    return f

nitf_diff.config["TRE"]["USE00A"] = {
    'eq_fun' : { 'rev_num' : compare_fixed_value(3200) }
}
