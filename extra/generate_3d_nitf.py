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

rows = 400
cols = 300
bands = 500

data = np.zeros((rows,cols, bands), dtype=np.dtype('>i2'))

def write_by_row_p(d, bstart, lstart, sstart):
    #print("sstart", sstart)
    for a in range(d.shape[0]):
        for b in range(d.shape[1]):
            #print(a*20+b*30)
            d[a, b] = a*20+b*30

def write_by_row_p_from_data(d, bstart, lstart, sstart):
    d[:, :] = data[lstart, :, :]

def create_16bit_image():
    # Write by column
    img3 = NitfImageWriteDataOnDemand(nrow=rows, ncol=cols, data_type=np.uint16,
                                      numbands=bands, data_callback=write_by_row_p_from_data,
                                      image_gen_mode=NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_ROW_P)

    ih = img3.image_subheader
    ih.nbpr = 1
    ih.nbpc = rows
    ih.nppbh = cols
    ih.nppbv = 1
    ih.imode = "P"
    ih.iid1 = '16bit img'
    segment = NitfImageSegment(img3)

    return segment

def create_float_image():
    # 32bit float image w large pixel values
    img3 = NitfImageWriteDataOnDemand(nrow=rows, ncol=cols, data_type=np.float32,
                                      numbands=bands, data_callback=write_by_row_p_from_data,
                                      image_gen_mode=NitfImageWriteDataOnDemand.IMAGE_GEN_MODE_ROW_P)
    ih = img3.image_subheader
    ih.nbpr = 1
    ih.nbpc = rows
    ih.nppbh = cols
    ih.nppbv = 1
    ih.imode = "P"
    ih.iid1 = 'float img'
    segment = NitfImageSegment(img3)

    return segment


if __name__ ==  "__main__":

    nitf_1 = 'sample_3d_nitf.ntf'

    f = NitfFile()

    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.5
    color = (255, 255, 255)
    thickness = 2

    #Write bands
    org = (100, 200)
    for b in range(bands):
        #print(data[:, :, b].shape)
        data2 = np.zeros((rows, cols), dtype=np.uint16)
        data[:,:,b] = cv2.putText(data2, 'Band #'+str(b), org, font,
                        fontScale, color, thickness, cv2.LINE_AA)

    # Write rows
    org = (100, 30)
    for r in range(rows):
        # print(data[:, :, b].shape)
        data2 = data[r,:,:].copy()
        data[r, :, :] = cv2.putText(data2, 'Row #' + str(r), org, font,
                        fontScale, color, thickness, cv2.LINE_AA)

    # Write cols
    org = (300, 300)
    for c in range(cols):
        #print(data[:, :, c].shape)
        data3 = data[:, c, :].copy()
        data[:, c, :] = cv2.putText(data3, 'Col #' + str(c), org, font,
                        fontScale, color, thickness, cv2.LINE_AA)

    # Displaying the image
    # plot = plt.imshow(data[:, :, 19])
    # plt.show()
    # plot = plt.imshow(data[:, 9, :])
    # plt.show()
    # for i in range(20):
    #     plot = plt.imshow(data[i,:,:])
    #     plt.show()

    f.image_segment.append(create_16bit_image())
    f.image_segment.append(create_float_image())

    # Now we write out to a nitf file
    f.write(nitf_1)


