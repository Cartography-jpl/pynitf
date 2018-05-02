from .nitf_image_subheader import (NitfImageSubheader,
                                   set_default_image_subheader)
import abc, six
import numpy as np

class NitfImageCannotHandle(RuntimeError):
    '''Exception that indicates we can't read a particular image. Note that
    this does *not* mean an error occured - e.g., a corrupt image. Rather this
    means that the image is a type we don't handle, e.g., JPEG-2000.'''
    def __init__(self, msg = "Can't handle this type of image"):
        RuntimeError.__init__(self, msg)
        
@six.add_metaclass(abc.ABCMeta)
class NitfImage(object):
    '''This contains a image that we want to read or write from NITF.

    This class supplies a basic interface, a specific type of image can
    derive from this class and supply some of the missing functionality.

    We take in the image subheader (a NitfImageSubheader object), derived
    classes should fill in details of the subheader.

    A image doesn't actually have to derive from NitfImage if for some
    reason that is inconvenient, we use the standard duck typing and
    any class that supplies the right functions can be used. But this
    base class supplies what the interface should be.

    Note that a NitfImage class doesn't need to handle all types of images
    (e.g., supporting reading JPEG-2000). If it can't handle reading 
    a particular image, it should throw a NitfImageCannotHandle exception. 
    The NitfImageSegment class will then just move on to next possible
    handler class.

    Also, many of the derived classes will support either reading or writing,
    but not both. 
    '''
    def __init__(self, image_subheader=None, header_size=None, data_size=None):
        self.image_subheader = image_subheader
        self.header_size = header_size
        self.data_size = data_size
        # Derived classes should fill in information

    # Derived classes may want to override this to give a more detailed
    # description of what kind of image this is.
    def __str__(self):
        return 'NitfImage'

    # Declare a few types that we would expect from a numpy array, since
    # we often want to treat a NitfImage as something close to a numpy array.
    @property
    def shape(self):
        return self.image_subheader.shape

    @property
    def dtype(self):
        return self.image_subheader.dtype

    # Few properties from image_subheader that we want at this level
    @property
    def idlvl(self):
        return self.image_subheader.idlvl

    @property
    def iid1(self):
        return self.image_subheader.iid1
    
    @abc.abstractmethod
    def read_from_file(self, fh):
        '''Read an image from a file. For larger images a derived class might
        want to not actually read in the data (e.g., you might memory
        map the data or otherwise generate a 'read on demand'), but at
        the end of the read fh should point past the end of the image data
        (e.g., do a fh.seek(start_pos + size of image) or something like 
        that)'''
        raise NotImplementedError()

    @abc.abstractmethod
    def write_to_file(self, fh):
        '''Write an image to a file.'''
        raise NotImplementedError()

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
    def __init__(self, image_subheader = None, header_size = None,
                 data_size = None):
        NitfImage.__init__(self,image_subheader, header_size, data_size)
        self.data_start = None
        
    def __str__(self):
        return "NitfImagePlaceHolder %d bytes of data" % (self.data_size)

    def read_from_file(self, fh):
        '''Read an image from a file. For larger images a derived class might
        want to not actually read in the data (e.g., you might memory
        map the data or otherwise generate a 'read on demand'), but at
        the end of the read fh should point past the end of the image data
        (e.g., do a fh.seek(start_pos + size of image) or something like 
        that)'''
        self.data_start = fh.tell()
        fh.seek(self.data_size, 1)

    def write_to_file(self, fh):
        '''Write an image to a file.'''
        raise NotImplementedError("Can't write a NitfImagePlaceHolder")

class NitfImageReadNumpy(NitfImageWithSubset):
    '''Implementation of NitfImage that reads data into a numpy array. We 
    can either read the data into memory, or do a memory map.

    This is a good default class. It does not handle blocked data or 
    compression however.
    '''
    def __init__(self, *args, **kwargs):
        '''Read data. If the keyword mmap=True, we memory map the data rather
        than reading it into memory (useful for larger files). Otherwise, we
        read directly into memory'''
        self.do_mmap = kwargs.pop('mmap', True)
        super().__init__(*args, **kwargs)
        self.data = None
        if self.image_subheader is None:
            self.image_subheader = NitfImageSubheader()

    def __getitem__(self, ind):
        return self.data[ind]

    def __str__(self):
        if(self.shape[0] == 1):
            print(self.dtype)
            return "NitfImageReadNumpy %d x %d %s image" % (self.shape[1], self.shape[2], str(self.dtype.newbyteorder("=")))
        return "NitfImageReadNumpy %d x %d x %d %s image" % (self.shape[0], self.shape[1], self.shape[2], str(self.dtype.newbyteorder("=")))

    def read_from_file(self, fh):
        '''Read from a file'''
        # Check if we can read the data.
        ih = self.image_subheader
        if(ih.ic != "NC"):
            raise NitfImageCannotHandle("Can only handle uncompressed images")
        if(ih.nbpr != 1 or ih.nbpc != 1):
            raise NitfImageCannotHandle("Cannot handle blocked data")
        # We could add support here for pixel or row interleave here if
        # needed, just need to work though juggling the data here.
        if(ih.imode != "B"):
            raise NitfImageCannotHandle("Currently only support block interleave")
        if(self.do_mmap):
            foff = fh.tell()
            self.data = np.memmap(fh, mode="r", dtype = ih.dtype,
                                  shape=self.shape,
                                  offset = foff)
            fh.seek(self.data.size * self.data.itemsize + foff, 0)
        else:
            self.data = np.fromfile(fh, dtype = ih.dtype,
                                    count=ih.nrows*ih.ncols*ih.number_band)
            self.data = np.reshape(self.data, self.shape)
        self.data_size = self.data.size * self.data.itemsize

    def write_to_file(self, fh):
        '''Write an image to a file.'''
        raise NotImplementedError("Can't write a NitfImageReadNumpy")

class NitfImageWriteDataOnDemand(NitfImageWithSubset):
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
                 generate_by_band=False):
        '''If generate_by_band=True, we call data_to_write a single band 
        at a time, otherwise we do everything at once. Depending on how
        the data is generated or its size this can be more or less efficient.

        You can pass a number of values to set in the image subheader. You
        can also just modify the image subheader after the constructor, 
        whatever is more convenient.

        Note that idlvl should be unique in a file, there are tools that 
        depend on this (plus the standard says that it should be unique).

        iid1 does *not* have to be unique, you can group similiar image 
        together by giving them the same iid1 (e.g., have a number of 
        "Radiance" image segments for multiple view from AirMSPI or something
        like that).'''
        super().__init__(NitfImageSubheader())
        set_default_image_subheader(self.image_subheader, nrow, ncol, data_type,
                                    numbands=numbands, iid1=iid1, iid2=iid2,
                                    idatim=idatim, irep=irep, icat=icat,
                                    idlvl=idlvl)
        self.data_callback = data_callback
        self.generate_by_band = generate_by_band

    def read_from_file(self, fh):
        '''Write an image to a file.'''
        raise NotImplementedError("Can't read a NitfImageWriteDataOnDemand")

    # Default is to call a supplied function. We can have derived classes
    # override this if desired.
    def data_to_write(self, d, bstart, lstart, sstart):
        self.data_callback(d, bstart, lstart, sstart)
        
    def write_to_file(self, fh):
        ih = self.image_subheader
        if(self.generate_by_band):
            d = np.zeros((1,ih.nrows, ih.ncols), dtype = ih.dtype)
            for b in range(ih.number_band):
                self.data_to_write(d, b, 0, 0)
                fh.write(d.tobytes())
        else:
            d = np.zeros((ih.number_band,ih.nrows, ih.ncols), dtype = ih.dtype)
            self.data_to_write(d, 0, 0, 0)
            fh.write(d.tobytes())
    
class NitfImageWriteNumpy(NitfImageWriteDataOnDemand):
    '''This is a simple implementation of a NitfImage where we just use 
    a numpy array to hold the data, and write that out.'''
    def __init__(self, nrow, ncol, data_type, **keywords):
        super().__init__(nrow, ncol, data_type, **keywords)
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

            
__all__ = ["NitfImageCannotHandle", "NitfImage", "NitfImagePlaceHolder",
           "NitfImageReadNumpy", "NitfImageWriteDataOnDemand",
           "NitfImageWriteNumpy", "NitfRadCalc"]

