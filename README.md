# Pynitf

## Introduction

This is a python module used to read and write NITF 2.1 files.

The module is extendable, you can add new TREs and can also tie in new objects
to manage TREs. See GeoCal, with the file geocal_nitf_rsm.py to see how this 
works.

## Callbacks

NITF is an old format, with all kinds of limitations. One limitation is that
we can't write out data until we are creating the whole file.

When generating data in a program for HDF, you naturally do a calculation, 
write the results field to HDF, and then continue to the next calculation.

For NITF on the other hand, we don't know where to write out an image segment
until we've written everthing before it. This is particularly true for 
compressed images, where we don't know the size of the previous image until
it has been generated, compressed, and writen to the NITF file.

There are a couple of ways to handle this. One is to use lots of intermediate
files and/or memory. So we generate all our data ahead of time, and then just
access it when we actually write out the NITF file.

An alternative is to generate data on demand. Rather than writing to a NITF 
file, we register various call back functions to generate the data when we
are ready for it. These callbacks then get called as we write out the file.




