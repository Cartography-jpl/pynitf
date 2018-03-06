# Just import any files we find in this directory, rather than listing
# everything

from __future__ import absolute_import
import os as _os
import glob as _glob

for _i in _glob.glob(_os.path.dirname(__file__) + "/*.py"):
    _mname = _os.path.basename(_i).split('.')[0]
    # Don't load ipython, which is ipython magic extensions
    if(not _mname == 'ipython'):
        exec("from .%s import *" % _mname)

del _i
del _mname
del _os
del _glob
        
