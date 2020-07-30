from .nitf_field import BytesFieldData, FieldStruct, FieldStructDiff
from .nitf_segment_data_handle import (NitfDes,
                                       NitfSegmentDataHandleSet)
from .nitf_diff_handle import NitfDiffHandle, NitfDiffHandleSet
from .nitf_segment_user_subheader_handle import desid_to_user_subheader_handle
import io
import os
import datetime
import shutil
import tempfile
import numpy as np
import warnings
import subprocess
import logging

# DesEXT_h5 depends on h5py being available. Ok if it isn't, we just can't
# use this particular class.
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import h5py
except ImportError:
    pass

hlp = '''This is NITF EXT_DEF_CONTENT DES. This is a new DES defined in NSGPDD-A).
'''

desc =[['content_headers_len', 'Length in bytes of the CONTENT_HEADERS field',
        4, int],
        ['content_headers', 'Metadata describing the embedded content',
         'f.content_headers_len', None,
         {'field_value_class' : BytesFieldData}]]

class DesExtContentHeader(FieldStruct):
    '''This handles the contents header portion of the DES. See Table 
    7.4.7.10.1-1 in NSGPDD-A Base U'''
    desc = desc
    
    hlist = [[b"Content-Type", "content_type"],
             [b"Content-Use", "content_use"],
             [b"Content-Encoding", "content_encoding"],
             [b"Content-Range", "content_range"],
             [b"Content-Length", "content_length"],
             [b"Content-Description", "content_description"],
             [b"Content-Disposition", "content_disposition"],
             [b"Canonical-ID", "canonical_id"],
             [b"DES-ID1", "des_id1"],
             [b"DES-ID2", "des_id2"],
             ]
             
    def __init__(self):
        super().__init__()
        self.content_type = b""
        self.content_use = b""
        self.content_encoding = None
        self.content_range = None
        self.content_length = b"0"
        self.content_description = b""
        self.content_disposition = b""
        self.canonical_id = b""
        self.des_id1 = b""
        self.des_id2 = b""
        self._des = None
        # For now, skip the optional things found in the table.

    def _snippet(self, name, var):
        v = getattr(self, var)
        if(v is None):
            return None
        return name + b": " + v

    def _set_snippet(self, k, v):
        for name, var in DesExtContentHeader.hlist:
            if(k == name):
                setattr(self, var, v)

    def bytes(self):
        t = [ self._snippet(nm, var) for (nm, var) in DesExtContentHeader.hlist ]
        return b'\r\n'.join([tv for tv in t if(tv is not None)]) + b'\r\n'

    def parse(self):
        for ln in self.content_headers.rstrip(b'\r\n').split(b'\r\n'):
            k, v = ln.split(b': ')
            self._set_snippet(k, v)
            
    def read_from_file(self, fh):
        super().read_from_file(fh)
        self.parse()

    def write_to_file(self, fh):
        if(self._des):
            self.content_length = str(self._des.data_size).encode('utf-8')
        self.content_headers = self.bytes()
        super().write_to_file(fh)
        
    def __str__(self):
        fh = io.StringIO()
        print("Content Header:", file=fh)
        for (nm, var) in DesExtContentHeader.hlist:
            t = self._snippet(nm, var)
            if(t):
                print("  " + t.decode('utf-8'), file=fh)
        return fh.getvalue()
    
class DesExtContentHeaderDiff(FieldStructDiff):
    '''Compare two user headers.'''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("DesExtContentHeader", {})

    def handle_diff(self, h1, h2, nitf_diff):
        with nitf_diff.diff_context("DesExtContentHeader"):
            if(not isinstance(h1, DesExtContentHeader) or
               not isinstance(h2, DesExtContentHeader)):
                return (False, None)
            return (True, self.compare_obj(h1, h2, nitf_diff))

NitfDiffHandleSet.add_default_handle(DesExtContentHeaderDiff())

_default_config = {}
 
NitfDiffHandleSet.default_config["DesExtContentHeader"] = _default_config

class DesEXT_DEF_CONTENT(NitfDes):
    '''This is the NITF EXT_DEF_CONTENT DES. This is a new DES defined in
    NSGPDD-A).'''
    uh_class = DesExtContentHeader
    des_tag = "EXT_DEF_CONTENT"
    def __init__(self, seg=None, data_size=None):
        super().__init__(seg)
        if(not seg):
            self.user_subheader._des = self
            self.data_size = data_size
        else:
            self.data_size = self._seg().data_size
        self.data = None

    def str_hook(self, file):
        print("DesEXT_DEF_CONTENT", file=file)

    def read_from_file(self, fh, seg_index=None):
        '''Read DES from file.

        This version doesn't actually read in the data (which might be
        large). Instead, it memory maps a numpy array to the data.
        '''
        if(self.subheader.desid != "EXT_DEF_CONTENT"):
            return False
        foff = fh.tell()
        self.data = np.memmap(fh, mode="r", dtype=np.int8,
                              shape=(self.data_size,), offset=foff)
        fh.seek(self.data.size + foff, 0)
        return True

    def write_to_file(self, fh):
        '''This is a dummy write operation. We just write self.data_size
        '0''s.'''
        if(self.data_size):
            fh.write(b'\0' * self.data_size)

    def summary(self):
        res = io.StringIO()
        print("DesEXT_DEF_CONTENT", file=res)
        return res.getvalue()

desid_to_user_subheader_handle.add_des_user_subheader("EXT_DEF_CONTENT",
                                                      DesExtContentHeader)

logger = logging.getLogger('nitf_diff')
class DesExtDefContentDiff(NitfDiffHandle):
    '''Compare two DesExt. This just does a binary comparison. Often
    that is all that we want, if this is from some external file usually
    it is better to use tools directly on the external file, and all that
    we care about for NITF is that this is different. 

    We frequently want to not consider this an error either. So if for
    example we have a copy of an external configuration h5 file, we don't
    directly care if the file changes. However, the default here is to
    treat this as an error.

    This takes configuration parameters:
       exclude - if true, don't compare anything but just succeed
       exclude_but_warn - of true, warn about differences but don't treat
          as a failure.
   '''
    def configuration(self, nitf_diff):
        return nitf_diff.config.get("DesExtDefContent", {})

    def compare_data(self, d1, d2, nitf_diff):
        c = self.configuration(nitf_diff)
        if(c.get('exclude', False)):
            return True
        if(c.get('exclude_but_warn', False)):
            if(not np.array_equal(d1.data, d2.data)):
                logger.difference_ignored("content is different")
            return True
        if(not np.array_equal(d1.data, d2.data)):
            logger.difference("content is different")
            return False
        return True
    
    def handle_diff(self, d1, d2, nitf_diff):
        with nitf_diff.diff_context("DesExtDefContent"):
            if(not isinstance(d1, DesEXT_DEF_CONTENT) or
               not isinstance(d2, DesEXT_DEF_CONTENT)):
                return (False, None)
            return (True, self.compare_data(d1, d2, nitf_diff))

NitfDiffHandleSet.add_default_handle(DesExtDefContentDiff())

_default_config = {}
 
NitfDiffHandleSet.default_config["DesExtDefContent"] = _default_config

class DesEXT_h5(DesEXT_DEF_CONTENT):
    def __init__(self, seg=None,file=None,
                 des_id1= b"h5file", des_id2= b"This is a h5 file",
                 temp_dir=None):
        super().__init__(seg)
        if(not seg):
            self.user_subheader.content_type = b"application/x-hdf5"
            self.user_subheader.des_id1 = des_id1
            self.user_subheader.des_id2 = des_id2
            self.data_size = None
        else:
            self.data_size = seg.data_size
        self.file = None
        if(file):
            self.attach_file(file)
        self.temp_dir = temp_dir
        self._h5py_fh = None

    def __str__(self):
        res = io.StringIO()
        self.str_hook(res)
        if(self.user_subheader):
            print("User-Defined Subheader: ", file=res)
            print(self.user_subheader, file=res)
        if self.h5py_fh is not None:
            h5lsoutput = subprocess.getoutput("h5ls -r %s" % self.h5py_fh.filename)
            print("HDF5 content", file=res)
            print(h5lsoutput, file=res)
        return res.getvalue()

    def attach_file(self, file):
        '''Attach a HDF 5 file to write out.'''
        self.file = file
        t = "attachment; filename=\"%s\"; creation-date=\"%s\"" % (os.path.basename(file), datetime.datetime.fromtimestamp(os.stat(file).st_ctime))
        self.user_subheader.content_disposition = t.encode("utf-8")
        self.data_size = os.path.getsize(file)

    @property
    def h5py_fh(self):
        '''Return a h5py file handle for reading the file.'''
        if(self._h5py_fh):
            return self._h5py_fh
        if(self.data is None):
            return None
        
        # Note that the very latest version of h5py (2.9) can be passed
        # a file handle like object, so we can read the data from the
        # NITF file w/o using a temporary. But older versions require
        # a temporary file.
        self.tfh = tempfile.NamedTemporaryFile(dir=self.temp_dir)
        self.data.tofile(self.tfh)
        self.tfh.flush()
        self._h5py_fh = h5py.File(self.tfh.name, "r")
        return self._h5py_fh

    def read_from_file(self, fh, seg_index=None):
        if(self.subheader.desid != "EXT_DEF_CONTENT"):
            return False
        if(self.user_subheader.content_type != b"application/x-hdf5"):
            return False
        super().read_from_file(fh, seg_index)
        return True
    
    def str_hook(self, file):
        print("DesEXT_h5", file=file)

    def summary(self):
        res = io.StringIO()
        print("DesEXT_h5", file=res)
        return res.getvalue()

    def write_to_file(self, fh):
        '''This is a dummy write operation. We just write self.data_size
        '0''s.'''
        if(self.file):
            with open(self.file, "rb") as fhin:
                shutil.copyfileobj(fhin, fh)
        elif (self.data is not None):
            fh.write(self.data)

# Try DesEXT_h5 before falling back to more generic DesEXT_DEF_CONTENT
NitfSegmentDataHandleSet.add_default_handle(DesEXT_DEF_CONTENT,
                                            priority_order=-1)
NitfSegmentDataHandleSet.add_default_handle(DesEXT_h5)

__all__ = ["DesEXT_DEF_CONTENT", "DesEXT_h5", "DesExtContentHeader"]
