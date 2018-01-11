from .nitf_image_subheader import NitfImageSubheader
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

class NitfImagePlaceHolder(NitfImage):
    '''Implementation that doesn't actually read any data, useful as a
    final place holder if none of our other NitfImage classes can handle
    a particular image.'''
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

class NitfImageFromNumpy(NitfImage):
    '''This is a simple implementation of a NitfImage where we just use 
    a numpy array to hold the data, and write that out. This is really just
    meant as a simple test case/example.

    This example is a byte, single band.'''
    def __init__(self, image_subheader = None, header_size = None,
                 data_size = None, nrow = None, ncol = None):
        if image_subheader is None:
            image_subheader = NitfImageSubheader()
        NitfImage.__init__(self,image_subheader, header_size, data_size)
        # Only fill in data if we give a size. Otherwise we assume
        # that we are doing to just do a read
        if(nrow is None):
            return
        self.data = np.zeros((nrow, ncol), dtype = np.uint8)
        ih = self.image_subheader
        ih.iid1 = "Test data"
        ih.iid2 = "This is from a NitfImageFromNumpy, used as sample data."
        ih.idatim = "20160101120000"
        ih.nrows = nrow
        ih.ncols = ncol
        ih.nbpr = 1
        ih.nbpc = 1
        ih.nppbh = ncol
        ih.nppbv = nrow
        ih.pvtype = "INT"
        ih.irep = "MONO"
        ih.icat = "VIS"
        ih.abpp = 8
        ih.nbpp = 8
        ih.ic = "NC"
        ih.nbands = 1
        ih.irepband[0] = 'M'

    def __str__(self):
        return "NitfImageFromNumpy %d x %d uint8 image" % (self.data.shape[0], self.data.shape[1])

    def read_from_file(self, fh):
        '''Read from a file'''
        # Sanity check that we can access this data
        ih = self.image_subheader
        if(ih.nbands != 1):
            raise NitfImageCannotHandle("Can only handle 1 band images")
        if(ih.ic != "NC"):
            raise NitfImageCannotHandle("Can only handle uncompressed images")
        if(ih.nbpr != 1 or ih.nbpc != 1):
            raise NitfImageCannotHandle("Cannot handle blocked data")
        if(ih.nbpp == 8):
            self.data = np.fromfile(fh, dtype=np.uint8, count=ih.nrows*ih.ncols)
        elif(ih.nbpp ==16):
            self.data = np.fromfile(fh, dtype=np.uint16,
                                    count=ih.nrows*ih.ncols)
        elif(ih.nbpp ==32):
            self.data = np.fromfile(fh, dtype=np.uint32,
                                    count=ih.nrows*ih.ncols)
        else:
            raise NitfImageCannotHandle("Unrecognized nbpp %d" % ih.nbpp)
        self.data = np.reshape(self.data, (ih.nrows,ih.ncols))

    def write_to_file(self, fh):
        '''Write to a file'''
        # Note that data is a single byte, so endianness isn't something
        # we need to worry about
        fh.write(self.data.tobytes())
        
class NitfImageGeneral(NitfImage):
    #This is a implementation of NitfImage that either takes binary numpy blob or generates
    #its own using specified value
    def __init__(self, image_subheader = None, header_size = None, data_size=None,
                 nrow = None, ncol = None, numbands=1, dataType=np.uint16, value=0, data=None):
        if image_subheader is None:
            image_subheader = NitfImageSubheader()
        if data_size == None:
            data_size = nrow*ncol*numbands*np.dtype(dataType).itemsize
        NitfImage.__init__(self,image_subheader, header_size, data_size)
        # Only fill in data if we give a size. Otherwise we assume
        # that we are doing to just do a read
        if(nrow is None):
            return
        self.data = data
        if (data == None):
            self.nrow = nrow
            self.ncol = ncol
            self.numbands = numbands
            self.value = value
            self.dataType = dataType
            #self.data = np.ndarray(shape=(nrow, ncol, numbands), dtype = dataType,
            #            buffer=np.array([value]*nrow*ncol*numbands))

        set_image_subheader(nrow, ncol, dataType, numbands)

    def __str__(self):
        if hasattr(self.data, 'shape'):
            return "NitfImageGeneral %d x %d, %d bands of type %s" \
                   % (self.data.shape[0], self.data.shape[1], self.data.shape[2], self.data.dtype)
        else:
            return "NitfImageGeneral %d x %d, %d bands, blob size %d" \
               % (self.image_subheader.nrows, self.image_subheader.ncols, self.image_subheader.nbands, self.data_size)

    def set_image_subheader(self, nrow, ncol, dataType, numbands):
        ih = self.image_subheader
        ih.iid1 = "Test data"
        ih.iid2 = "This is from a NitfImageFromNumpy, used as sample data."
        ih.idatim = "20160101120000"
        ih.nrows = nrow
        ih.ncols = ncol
        ih.nbpr = 1
        ih.nbpc = 1
        ih.nppbh = ncol
        ih.nppbv = nrow

        if (dataType == np.uint8):
            ih.abpp = 8
            ih.nbpp = 8
            ih.pvtype = "INT"
        elif (dataType == np.uint16):
            ih.abpp = 16
            ih.nbpp = 16
            ih.pvtype = "INT"
        elif (dataType == np.float32):
            ih.abpp = 32
            ih.nbpp = 32
            ih.pvtype = "R"
        elif (dataType == np.float64):
            ih.abpp = 64
            ih.nbpp = 64
            ih.pvtype = "R"
        else:
            raise NitfImageCannotHandle("Unsupported dataType")

        ih.ic = "NC"

        if (numbands < 10):
            ih.nbands = numbands
        else:
            ih.nbands = 0
            ih.xbands = numbands

        for b in range(numbands):
            ih.irepband[b] = 'M'
            ih.isubcat[b] = b + 1
            ih.nluts[b] = 0

        # If numbands is 1, we end up with the irepband being "R"
        ih.irepband[numbands - 1] = "B"
        ih.irepband[int(numbands / 2)] = "G"
        ih.irepband[0] = "R"

    #Todo: Since we don't store the data in self.data anymore,
    #We need to now provide data accessor functions instead of allowing for direct
    #self.data access
    def read_from_file(self, fh):
        '''Read from a file'''
        ih = self.image_subheader

        #Instead of reading the entire data in memory, which could be gigabytes,
        #we will simply note the location and size of the data in the input file
        # Todo: Reading from it is not thread-safe right now
        self.data = (fh.name, fh.tell(), self.data_size)#fh.read(self.data_size)

        #We need to move the file pointer to the next section
        fh.seek(self.data_size, 1)

    def write_to_file(self, fh):
        '''Write to a file'''
        # Note that data is a single byte, so endianness isn't something
        # we need to worry about

        #If the data is none, that means that we just stored parameters to
        #use to generate quick data
        if (self.data == None):
            bytes = np.ndarray(shape=(self.nrow, self.ncol),
                buffer=np.array([self.value] * self.nrow *self.ncol, self.dataType),
                dtype=self.dataType).tobytes()
            for b in range(self.numbands):
                fh.write(bytes)

        #If data is a tuple, that means we saved the file information to
        #use to write data.
        elif (type(self.data) is tuple):
            filename = self.data[0]
            location = self.data[1]
            size = self.data[2]

            blockSize = 1024
            inFile = open(filename, 'rb')
            inFile.seek(location)
            while (size > 0):
                if (size < blockSize):
                    blockSize = size
                inData = inFile.read(blockSize)
                fh.write(inData)
                size = size - blockSize

            inFile.close()

        else:
            fh.write(self.data.tobytes())
