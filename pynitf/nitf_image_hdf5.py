from .nitf_image import NitfImage
from .nitf_image_subheader import NitfImageSubheader
import abc, six
import numpy as np
        
class NitfImageHDF5(NitfImage):
    #This is a implementation of NitfImage that either takes HDF5 numpy image
    def __init__(self, data, image_subheader = None, bands=None, nrow=None):
        if image_subheader is None:
            image_subheader = NitfImageSubheader()

        NitfImage.__init__(self,image_subheader, header_size, data_size)

        self.data = data

        if(nrow is None):
            nrow = data.shape[0]
        ncol = data.shape[1]

        dataType = data.dtype

        set_image_subheader(nrow, ncol, dataType, numbands)

        ih = self.image_subheader
        ih.iid1 = "HDF5 data"
        ih.iid2 = "This is from a NitfImageHDF5/numpy."
        ih.idatim = "20160101120000"

    def __str__(self):
        return "NitfImageHFD5 %d x %d, %d bands, blob size %d" \
            % (self.image_subheader.nrows, self.image_subheader.ncols, self.image_subheader.nbands, self.data_size)

    def bands(self):
        bands = self.image_subheader.nbands
        if (bands == 0):
            bands = self.image_subheader.xbands

        return bands

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

    def writeFullRow(self, fh, data, h_low, h_high, v_low, v_high):
        modLow = h_low % (data.shape[0] + 1)
        modHigh = h_high % (data.shape[0] + 1)
        if (modHigh >= modLow):
            fh.write(data[modLow:modHigh, v_low:v_high].tobytes())
        else:
            fh.write(data[modLow:, v_low:v_high].tobytes())
            fh.write(data[:modHigh, v_low:v_high].tobytes())

    def writePartialRows(self, fh, data, v_low, v_high, h_low, h_high):
        ih = self.image_header

        npixels = v_high - ih.ncols
        fillData = np.ndarray(shape=(npixels, self.bands()),
                              buffer=np.array([0] * (npixels * self.bands()), data.dtype), dtype=data.dtype)
        print(fillData.shape)

        for i in range(h_low, h_high):
            fh.write(data[i, v_low:ih.ncols].tobytes())
            fh.write(fillData.tobytes)

    def writeEmptyRows(self, fh, data, h_high):
        ih = self.image_subheader

        fillData = np.ndarray(shape=(h_high - ih.nrows, ih.nppbv, self.bands()),
                              buffer=np.array([0] * ((h_high - ih.nrows) * ih.nppbv * self.bands()),
                                              data.dtype), dtype=data.dtype)
        print(fillData.shape)
        fh.write(fillData.tobytes)

    def write_to_file(self, fh):
        '''Write to a file'''

        # Make sure the data is written in big-endian
        # WARNING! The following comparison only works on Intel (little-endian) processors.
        #          I don't have access to a big-endian processor so have not implemented for it
        # NOTE: Currently we are preserving the original data in the original endian-form
        #       and that causes memory requirement to double. Not sure if that's necessary
        if (self.data.dtype.byteorder == '='):
            print("Little-endian architecture detected. Changing to big-endian...")
            data = self.data.byteswap()
        else:
            data = self.data

        ih = self.image_subheader
        bands = self.bands()

        for i in range(ih.nbpr):
            for j in range(ih.nbpc):
                h_low = i * ih.nppbv
                h_high = (i + 1) * ih.nppbv
                v_low = j * ih.nppbh
                v_high = (j + 1) * ih.nppbh

                #If both dimensions don't fall on the block boundaries, need to zero fill
                #both horizontally and vertically
                # ---------___
                # ---------___
                # ---------___
                # ____________
                # ____________
                if (h_high > ih.nrows and v_high > ih.ncols):
                    print("%d is larger than %d, horizontally and \
                          %d is larger than %d, vertically" %
                          (h_high, ih.nrows, v_high, ih.ncols))

                    #modLowH = h_low % (data.shape[0] + 1)
                    #modHighH = h_high % (data.shape[0] + 1)
                    #modLowV = v_low % (data.shape[1] + 1)
                    #modHighV = v_high % (data.shape[1] + 1)

                    #if (modHighH < modLowH or modHighV > modLowV):
                    #    raise NitfImageCannotHandle(
                    #        "Currently we cannot repeat images horizontally: %d is greater than %d" % (
                    #        v_high, data.shape[1]))
                    #else:
                        #First we zero fill the rows of the missing columns interleaved with rows that
                        #exist in the data. In the illustration above, it'd be the first 3 rows
                    writePartialRows(fh, data, v_low, v_high, h_low, ih.nrows)

                        #Then we will zero fill the entire rows where no information exists.
                        #This is the last 2 rows in the illustration above
                    self.writeEmptyRows(fh, data, h_high)

                #Else if we are short just on rows, zero fill just horizontally
                # ------------
                # ------------
                # ------------
                # ____________
                # ____________
                elif (h_high > ih.nrows):
                    print("%d is larger than %d, horizontally" % (h_high, ih.nrows))
                    self.writeFullRow(fh, data, h_low, ih.nrows, v_low, v_high)

                    self.writeEmptyRows(fh, data, h_high)

                #Else if we are short just on cols, zero fill just vertically
                #Since we're writing rows first, we will have to interleave the fill rows every column
                # ---------___
                # ---------___
                # ---------___
                # ---------___
                # ---------___
                elif (v_high > ih.ncols):
                    print("%d is larger than %d, vertically" % (v_high, ih.ncols))
                    #modLow = v_low % (data.shape[1] + 1)
                    #modHigh = v_high % (data.shape[1] + 1)

                    #if (modHigh >= modLow):
                    writePartialRows(fh, data, v_low, v_high, h_low, h_high)
                    #else:
                    #    raise NitfImageCannotHandle("Currently we cannot repeat images horizontally: %d is greater than %d" % (v_high, data.shape[1]))

                #Else, we're at exact match on both dimensions along block boundaries
                # ------------
                # ------------
                # ------------
                # ------------
                # ------------
                else:
                    print("we're at exact match on both dimensions along block boundaries")
                    self.writeFullRow(fh, data, h_low, h_high, v_low, v_high)
