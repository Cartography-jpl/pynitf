from .nitf_field import *
from .nitf_des import *
import io
import os
import datetime
import shutil
import tempfile
import numpy as np
import warnings

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

desc =[['content_headers_len', 'Length in bytes of the CONTENT_HEADERS field', 4, int],
        ['content_headers', 'Metadata describing the embedded content', 'f.content_headers_len', None,
          {'field_value_class' : StringFieldData}]]

DesEXT_DEF_CONTENT_UH = create_nitf_field_structure("DesEXT_DEF_CONTENT_UH",
       desc, hlp = "This is the user defined subheader for DesEXT_DEF_CONTENT")

class DesEXTContentHeader(object):
    '''This handles the contents header portion of the DES. See Table 
    7.4.7.10.1-1 in NSGPDD-A Base U'''
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
        # For now, skip the optional things found in the table.

    def _snippet(self, name, var):
        v = getattr(self, var)
        if(v is None):
            return None
        return name + b": " + v

    def _set_snippet(self, k, v):
        for name, var in DesEXTContentHeader.hlist:
            if(k == name):
                setattr(self, var, v)

    def bytes(self):
        t = [ self._snippet(nm, var) for (nm, var) in DesEXTContentHeader.hlist ]
        return b'\r\n'.join([tv for tv in t if(tv is not None)]) + b'\r\n'

    def parse(self, s):
        for ln in s.rstrip(b'\r\n').split(b'\r\n'):
            k, v = ln.split(b': ')
            self._set_snippet(k, v)

    def __str__(self):
        fh = io.StringIO()
        print("Content Header:", file=fh)
        for (nm, var) in DesEXTContentHeader.hlist:
            t = self._snippet(nm, var)
            if(t):
                print("  " + t.decode('utf-8'), file=fh)
        return fh.getvalue()
            

class DesEXT_DEF_CONTENT(NitfDes):
    '''This is the NITF EXT_DEF_CONTENT DES. This is a new DES defined in
    NSGPDD-A).'''
    def __init__(self, des_subheader = None, header_size=None,
                 data_size=None, user_subheader=None):
        super().__init__(des_id="EXT_DEF_CONTENT",
                         des_subheader=des_subheader,
                         header_size=header_size, data_size=data_size,
                         user_subheader=user_subheader,
                         user_subheader_class=DesEXT_DEF_CONTENT_UH)
        if(self.des_subheader.desid != "EXT_DEF_CONTENT"):
            raise NitfDesCannotHandle()
        self.content_header = DesEXTContentHeader()
        if(user_subheader):
            self.content_header.parse(user_subheader.content_headers)
        self.data = None

    def str_hook(self, file):
        print("DesEXT_DEF_CONTENT", file=file)

    def __str__(self):
        fh = io.StringIO()
        self.str_hook(fh)
        print(self.content_header, file=fh)
        return fh.getvalue()

    def read_user_subheader(self):
        super().read_user_subheader()
        self.content_header.parse(self.user_subheader.content_headers)

    def read_from_file(self, fh):
        '''Read DES from file.

        This version doesn't actually read in the data (which might be
        large). Instead, it memory maps a numpy array to the data.
        '''
        self.read_user_subheader()
        foff = fh.tell()
        self.data = np.memmap(fh, mode="r", dtype=np.int8,
                              shape=(self.data_size,), offset=foff)
        fh.seek(self.data.size + foff, 0)

    def write_to_file(self, fh):
        '''This is a dummy write operation. We just write self.data_size
        '0''s.'''
        if(self.data_size):
            fh.write(b'\0' * self.data_size)

    def write_user_subheader(self, sh):
        self.content_header.content_length = str(self.data_size).encode('utf-8')
        self.user_subheader.content_headers = self.content_header.bytes()
        super().write_user_subheader(sh)
        
    def summary(self):
        res = io.StringIO()
        print("DesEXT_DEF_CONTENT", file=res)
        return res.getvalue()
        

class DesEXT_h5(DesEXT_DEF_CONTENT):
    def __init__(self, file = None, des_subheader = None, header_size=None,
                 data_size=None, user_subheader=None,
                 des_id1= b"h5file", des_id2= b"This is a h5 file",
                 temp_dir=None):
        super().__init__(des_subheader = des_subheader, header_size=header_size,
                         data_size=data_size, user_subheader=user_subheader)
        self.content_header.content_type = b"application/x-hdf5"
        
        if(not user_subheader):
            self.content_header.des_id1 = des_id1
            self.content_header.des_id2 = des_id2
        self.file = None
        if(file):
            self.attach_file(file)
        self.temp_dir = temp_dir
        self._h5py_fh = None

    def attach_file(self, file):
        '''Attach a HDF 5 file to write out.'''
        self.file = file
        t = "attachment; filename=\"%s\"; creation-date=\"%s\"" % (os.path.basename(file), datetime.datetime.fromtimestamp(os.stat(file).st_ctime))
        self.content_header.content_disposition = t.encode("utf-8")
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
        
    def read_user_subheader(self):
        super().read_user_subheader()
        if(self.content_header.content_type != b"application/x-hdf5"):
            raise NitfDesCannotHandle()
        
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
register_des_class(DesEXT_DEF_CONTENT, priority_order=-1)
register_des_class(DesEXT_h5)

__all__ = ["DesEXT_DEF_CONTENT", "DesEXT_DEF_CONTENT_UH",
           "DesEXT_h5", "DesEXTContentHeader"]
