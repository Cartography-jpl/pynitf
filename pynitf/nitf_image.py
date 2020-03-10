from .nitf_image_subheader import (NitfImageSubheader,
                                   set_default_image_subheader)
from .nitf_segment_data_handle import (NitfImage, NitfSegmentDataHandleSet)
from .nitf_security import security_unclassified
from .nitf_diff_handle import (NitfDiffHandle, NitfDiffHandleSet)
from .weak_key_value_dict import WeakKeyValueDict
import numpy as np
import mmap
import logging

class NitfImageWithSubset(NitfImage):
    '''It is common for a NitfImage to allow reading a subset of the data. 
    This is important for example to support blocking, or if 
    we just don't want to read the full. This also gives support for writing
    data where the data is supplied on demand from a data_to_write function
    for a given subset.

    This class provides this interface.
    '''
    def __str__(self):
        return 'NitfImageWithSubset'

    def __getitem__(self, ind):
        '''Return data read from image segment. This takes band, line, and
        sample or line, sample. Because it is so common, we can take
        only 2 values, and assume the band number is held at 0. This
        is useful, because the 1 band case is common.Line, sample,
        band can be a slice or an integer.  This should return
        something like a numpy array
        '''
        raise NotImplementedError()

    def data_to_write(self, d, bstart, lstart, sstart):
        '''Determine the data that we want to write, filling in the numpy
        array 'd', which is already the size that we expect. Start the
        block at lstart, sstart, bstart.

        This is then used by write_to_file to determine that data that we
        will write.'''
        raise NotImplementedError()

class NitfImagePlaceHolder(NitfImage):
    '''Implementation that doesn't actually read any data, useful as a
    final place holder if none of our other NitfImage classes can handle
    a particular image. We just skip over the data when reading.'''
    
    def __str__(self):
        return "NitfImagePlaceHolder %d bytes of data" % (self._seg().data_size)

    def __eq__(self, other):
        if not isinstance(other, NitfImagePlaceHolder):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.subheader == other.subheader

    def read_from_file(self, fh, segindex=None):
        '''Read an image from a file. For larger images a derived class might
        want to not actually read in the data (e.g., you might memory
        map the data or otherwise generate a 'read on demand'), but at
        the end of the read fh should point past the end of the image data
        (e.g., do a fh.seek(start_pos + size of image) or something like 
        that)'''
        self.data_start = fh.tell()
        self.fh_in_name = fh.name
        fh.seek(self._seg().data_size, 1)
        # Save, in case we are copying
        self._data_size = self._seg().data_size
        return True

    def write_to_file(self, fh):
        '''Write an image to a file.'''
        bytes_left = self._data_size
        buffer_size = 1024*1024
        with open(self.fh_in_name, 'rb') as fh_in:
            fh_in.seek(self.data_start)
            while(bytes_left > 0):
                if bytes_left < buffer_size:
                    d = fh_in.read(bytes_left)
                else:
                    d = fh_in.read(buffer_size)
                fh.write(d)

                #This may go negative on the last loop but that's fine
                bytes_left = bytes_left - buffer_size

logger = logging.getLogger('nitf_diff')
class ImagePlaceHolderDiff(NitfDiffHandle):
    def handle_diff(self, d1, d2, nitf_diff):
        if(not isinstance(d1, NitfImagePlaceHolder) or
           not isinstance(d2, NitfImagePlaceHolder)):
            return (False, None)
        logger.warn("Skipping image '%s', don't know how to read it.",
                    d1.subheader.iid1)
        return (True, True)

NitfDiffHandleSet.add_default_handle(ImagePlaceHolderDiff())
    
class NitfImageReadNumpy(NitfImageWithSubset):
    '''Implementation of NitfImage that reads data into a numpy array. We 
    can either read the data into memory, or do a memory map.

    This is a good default class. It does not handle blocked data or 
    compression however.
    '''

    # Keep a list of mmap associated with a filehandle. If either the
    # mmap or the filehandle disappears, this gets removed from this
    # dict
    mmap_cache = WeakKeyValueDict()
    
    def __init__(self, *args, **kwargs):
        '''Read data. If the keyword mmap=True, we memory map the data rather
        than reading it into memory (useful for larger files). Otherwise, we
        read directly into memory'''
        self.do_mmap = kwargs.pop('mmap', True)
        super().__init__(*args, **kwargs)
        self.data = None

    def __getitem__(self, ind):
        return self.data[ind]

    def __str__(self):
        if(self.shape[0] == 1):
            return "NitfImageReadNumpy %d x %d %s image" % (self.shape[1], self.shape[2], str(self.dtype.newbyteorder("=")))
        return "NitfImageReadNumpy %d x %d x %d %s image" % (self.shape[0], self.shape[1], self.shape[2], str(self.dtype.newbyteorder("=")))

    def read_from_file(self, fh, segindex=None):
        '''Read from a file'''

        # Save the file handle and data start location in the file because
        # it will come in handy later
        self.data_start = fh.tell()
        self.fh_in_name = fh.name

        # Check if we can read the data.
        ih = self.subheader
        if(ih.ic != "NC"):
            return False
        if(ih.nbpr != 1 or ih.nbpc != 1):
            return False
        # We could add support here for pixel or row interleave here if
        # needed, just need to work though juggling the data here.
        if(ih.imode != "B" and ih.imode != "P"):
            return False
        # Likewise, we don't work with 1 bit data
        if(ih.nbpp == 1):
            return False
        # Finally, there may be some weird combination of nbpp and pvtype
        # that we don't recognize. In this case, skip handling
        try:
            dt = ih.dtype
        except RuntimeError:
            return False
        if(self.do_mmap):
            if(fh not in self.mmap_cache):
                self.mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
                self.mmap_cache[fh] = self.mm
            else:
                self.mm = self.mmap_cache[fh]
            foff = fh.tell()
            self.data = np.ndarray(self.shape, dtype = ih.dtype,
                                   buffer = self.mm,
                                   offset = foff)
            fh.seek(self.data.size * self.data.itemsize + foff, 0)
        else:
            self.data = np.fromfile(fh, dtype = ih.dtype,
                                    count=ih.nrows*ih.ncols*ih.number_band)
            self.data = np.reshape(self.data, self.shape)
        self.data_size = self.data.size * self.data.itemsize
        return True

    def write_to_file(self, fh):
        '''Write an image to a file.'''
        bytes_left = self.data_size
        buffer_size = 1024*1024
        with open(self.fh_in_name, 'rb') as fh_in:
            fh_in.seek(self.data_start)
            while(bytes_left > 0):
                if bytes_left < buffer_size:
                    d = fh_in.read(bytes_left)
                else:
                    d = fh_in.read(buffer_size)
                fh.write(d)

                #This may go negative on the last loop but that's fine
                bytes_left = bytes_left - buffer_size

class ImageReadNumpyDiff(NitfDiffHandle):
    def handle_diff(self, d1, d2, nitf_diff):
        if(not isinstance(d1, NitfImageReadNumpy) or
           not isinstance(d2, NitfImageReadNumpy)):
            return (False, None)
        is_same = True
        t1 = d1[:,:,:]
        t2 = d2[:,:,:]
        # TODO Expose tolerance as configuration parameters
        if(t1.shape != t2.shape):
            logger.difference("Image '%s' shape different: %s != %s",
                              d1.subheader.iid1, t1.shape, t2.shape)
            is_same = False
        elif(not np.allclose(t1, t2)):
            logger.difference("Image '%s' is different",
                              d1.subheader.iid1)
            is_same = False
        # TODO Copy over other work by Derek, currently in
        # nitf_diff_support
        return (True, is_same)

NitfDiffHandleSet.add_default_handle(ImageReadNumpyDiff())
                

class NitfImageWriteDataOnDemand(NitfImageWithSubset):

    IMAGE_GEN_MODE_ALL = 0 #Write out pixel-by-pixel, not recommended because it's going to be very slow
    IMAGE_GEN_MODE_BAND = 1 #Write out one band at a time
    IMAGE_GEN_MODE_ROW_B = 2 #Write out one row at a time, bands first
    IMAGE_GEN_MODE_ROW_P = 3 #Write out one row at a time, pixel first
    IMAGE_GEN_MODE_COL_B = 4 #Write out one column at a time, bands first
    IMAGE_GEN_MODE_COL_P = 5 # Write out one column at a time, pixel first

    '''This writes a NitfImage where we generate the data on demand when
    we need to write the data out. A function should be registered to
    generate this data, or alternatively a class that derives from this one
    can override the data_to_write function'''
    def __init__(self, nrow, ncol, data_type, data_callback=None,
                 numbands=1,
                 iid1 = "Test data", iid2 = "This is sample data",
                 idatim = "20160101120000",
                 irep="MONO",
                 icat="VIS",
                 idlvl = 0,
                 image_gen_mode=IMAGE_GEN_MODE_ALL,
                 security=security_unclassified):
        '''If generate_by_band==True, we call data_to_write a single band 
        at a time, otherwise we do everything at once. Depending on how
        the data is generated or its size this can be more or less efficient.
        
        If generate_by_column==True, we call data_to_write a single column
        at a time. This would make sense if we have multi-band images that
        come in numerous "slices"

        You can pass a number of values to set in the image subheader. You
        can also just modify the image subheader after the constructor, 
        whatever is more convenient.

        Note that idlvl should be unique in a file, there are tools that 
        depend on this (plus the standard says that it should be unique).

        iid1 does *not* have to be unique, you can group similiar image 
        together by giving them the same iid1 (e.g., have a number of 
        "Radiance" image segments for multiple view from AirMSPI or something
        like that).'''
        super().__init__()
        set_default_image_subheader(self._shared_header.subheader, nrow,
                                    ncol, data_type,
                                    numbands=numbands, iid1=iid1, iid2=iid2,
                                    idatim=idatim, irep=irep, icat=icat,
                                    idlvl=idlvl)
        self.security = security
        self.data_callback = data_callback
        self.image_gen_mode = image_gen_mode

    def read_from_file(self, fh, segindex=None):
        '''Write an image to a file.'''
        raise NotImplementedError("Can't read a NitfImageWriteDataOnDemand")

    # Default is to call a supplied function. We can have derived classes
    # override this if desired.
    def data_to_write(self, d, bstart, lstart, sstart):
        self.data_callback(d, bstart, lstart, sstart)
        
    def write_to_file(self, fh):
        ih = self.subheader

        if (self.image_gen_mode == NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_ALL):
            d = np.zeros((ih.number_band,ih.nrows, ih.ncols), dtype = ih.dtype)
            self.data_to_write(d, 0, 0, 0)
            fh.write(d.tobytes())

        elif(self.image_gen_mode == NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_BAND):
            d = np.zeros((ih.nrows, ih.ncols), dtype = ih.dtype)
            for b in range(ih.number_band):
                self.data_to_write(d, b, 0, 0)
                fh.write(d.tobytes())

        elif (self.image_gen_mode == NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_ROW_B):
            d = np.zeros((ih.number_band, ih.ncols), dtype=ih.dtype)
            for r in range(ih.nrows):
                self.data_to_write(d, 0, r, 0)
                fh.write(d.tobytes())

        elif (self.image_gen_mode == NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_ROW_P):
            d = np.zeros((ih.ncols, ih.number_band), dtype=ih.dtype)
            for r in range(ih.nrows):
                self.data_to_write(d, 0, r, 0)
                fh.write(d.tobytes())

        elif (self.image_gen_mode == NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_COL_B):
            d = np.zeros((ih.number_band, ih.nrows), dtype=ih.dtype)
            for c in range(ih.ncols):
                self.data_to_write(d, 0, 0, c)
                fh.write(d.tobytes())

        elif (self.image_gen_mode == NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_COL_P):
            d = np.zeros((ih.nrows, ih.number_band), dtype=ih.dtype)
            for c in range(ih.ncols):
                self.data_to_write(d, 0, 0, c)
                fh.write(d.tobytes())
        else:
            raise RuntimeError("Incorrect Image Gen Mode %d" % self.image_gen_mode)
    
class NitfImageWriteNumpy(NitfImageWriteDataOnDemand):
    '''This is a simple implementation of a NitfImage where we just use 
    a numpy array to hold the data, and write that out.'''
    def __init__(self, nrow, ncol, data_type, **keywords):
        super(NitfImageWriteNumpy, self).__init__(nrow, ncol, data_type, **keywords)
        self._data = np.zeros(self.shape, dtype = data_type)

    def __getitem__(self, ind):
        return self._data[ind]

    def __setitem__(self, ind, v):
        self._data[ind] = v

    def __str__(self):
        if(self.shape[0] == 1):
            return "NitfImageWriteNumpy %d x %d %s image" % (self.shape[1], self.shape[2], str(self.dtype.newbyteorder("=")))
        return "NitfImageWriteNumpy %d x %d x %d %s image" % (self.shape[0],self.shape[1], self.shape[2], str(self.dtype.newbyteorder("=")))

    def data_to_write(self, d, bstart, lstart, sstart):
        d[:,:,:] = self._data[bstart:(bstart+d.shape[0]),lstart:(lstart+d.shape[1]),sstart:(sstart+d.shape[2])]


class NitfRadCalc(object):
    '''Sample calculation class, that shows how we can generate data on 
    demand. See unit test for an example of this.'''
    def __init__(self, dn_img, gain_img, offset_img):
        '''Constructor. Takes images for DN, gain, and offset which should
        supply the data as something like a numpy array or something
        derived from NitfImageWithSubset. We pretty much need a __getitem__
        that can take slices'''
        self.dn = dn_img
        self.gain = gain_img
        self.offset = offset_img

    def data_to_write(self, d, bstart, lstart, sstart):
        bs = slice(bstart, bstart + d.shape[0])
        ls = slice(lstart, lstart + d.shape[1])
        ss = slice(sstart, sstart + d.shape[2])
        d[:,:,:] = self.dn[bs,ls,ss] * self.gain[bs,ls,ss] + self.offset[bs,ls,ss]

NitfSegmentDataHandleSet.add_default_handle(NitfImageReadNumpy)
NitfSegmentDataHandleSet.add_default_handle(NitfImagePlaceHolder,
                                            priority_order= -1000)
        
__all__ = ["NitfImageWithSubset", "NitfImagePlaceHolder",
           "NitfImageReadNumpy", "NitfImageWriteDataOnDemand",
           "NitfImageWriteNumpy", "NitfRadCalc"]

