#! /usr/bin/env python

# Quick code to generate a 3-D cube writing in P mode using 1 row of data as a block.
# As of Feb 21, 2020 it's not been tested.
# Writes out text for each row, col, and band so that they will display correctly if a)
# the images have been written out correctly and b) if it's being rendered correctly

import copy
import json
import six
import numpy as np
import hashlib
import h5py
import time
import os
import cv2
import matplotlib.pyplot as plt
from pynitf import *

def write_by_row_p(d, bstart, lstart, sstart):
    #print("sstart", sstart)
    for a in range(d.shape[0]):
        for b in range(d.shape[1]):
            #print(a*20+b*30)
            d[a, b] = a*20+b*30

def write_by_row_p_from_data(d, bstart, lstart, sstart):
    d[:, :] = data[:, lstart, :]

def create_16bit_image():
    # Write by column
    img3 = NitfImageWriteDataOnDemand(nrow=400, ncol=300, data_type=np.dtype('>i2'),
                                      numbands=500, data_callback=write_by_row_p_from_data,
                                      image_gen_mode=NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_ROW_P)

    #TODO: Make sure that the blocking is correct
    ih = img3.image_subheader
    ih.nbpr = 1
    ih.nbpc = 300
    ih.nppbh = 400
    ih.nppbv = 1
    ih.imode = "P"
    ih.iid1 = '16bit img'
    segment = NitfImageSegment(img3)

    return segment

def create_float_image():
    # 32bit float image w large pixel values
    img3 = NitfImageWriteDataOnDemand(nrow=400, ncol=300, data_type=np.dtype('>f'),
                                      numbands=500, data_callback=write_by_row_p,
                                      image_gen_mode=NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_ROW_P)
    ih = img3.image_subheader
    ih.nbpr = 300
    ih.nbpc = 1
    ih.nppbh = 1
    ih.nppbv = 400
    ih.imode = "P"
    ih.iid1 = 'float img'
    segment = NitfImageSegment(img3)

    return segment


if __name__ ==  "__main__":

    bands = 500
    rows = 400
    cols = 300

    nitf_1 = 'sample_3d_nitf.ntf'

    f = NitfFile()

    data = np.zeros((cols,rows,bands), dtype=np.dtype('>i2'))

    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (150, 30)
    fontScale = 0.5
    color = (255, 0, 0)
    thickness = 2

    #Write bands
    for b in range(bands):
        #print(data[:, :, b].shape)
        data2 = np.zeros((cols, rows), dtype=np.dtype('>i2'))
        data[:,:,b] = cv2.putText(data2, 'Band #'+str(b), org, font,
                        fontScale, color, thickness, cv2.LINE_AA)

    # Write rows
    for r in range(rows):
        # print(data[:, :, b].shape)
        data2 = data[:,r,:]
        data[:, r, :] = cv2.putText(data2, 'Row #' + str(r), org, font,
                        fontScale, color, thickness, cv2.LINE_AA)

    # Write rows
    for c in range(cols):
        # print(data[:, :, b].shape)
        data2 = data[c, :, :]
        data[c, :, :] = cv2.putText(data2, 'Col #' + str(c), org, font,
                        fontScale, color, thickness, cv2.LINE_AA)

    # Displaying the image
    '''plot = plt.imshow(data[:, :, 17])
    plt.show()
    plot = plt.imshow(data[:, 17, :])
    plt.show()
    plot = plt.imshow(data[17, :, :])
    plt.show()'''

    f.image_segment.append(create_16bit_image())
    f.image_segment.append(create_float_image())

    # Now we write out to a nitf file
    f.write(nitf_1)


