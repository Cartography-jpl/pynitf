****************************************************
Design principles
****************************************************

Design Philosophy
=================

The overall design principle’s I had with pynitf:

#. Things that are format related should be handled by the library. So
   things like formatting floating point number into specific strings,
   adding padding for being the right length, etc. get handled by the
   library.

#. Things that are related to interpreting the data get handled by the
   library. So for example fields that give the length of a another field
   or the type of another field should be handled by the library. The
   idea is that the stuff needs to be consistent, it is too easy to
   create an invalid file if the end user is mucking with the internals
   (so saying a field is “byte”, but then writing it out as “floats”).

#. Things that are more a single “thing” get read/written as a
   whole. So examples of this are the camera and RSM, which have lots of
   individual fields but are really just one “thing” get read and written
   as “f.rsm” or “f.camera”. I think there classification stuff may fall
   into this category also - there are lots of fields associated with the
   the classification level but this is really just one thing.

#. Some things might get extended downstream. I guess I would think of
   this as added to the library downstream, but really part of the
   library. So things like project specific TREs might be added by the
   user of the library (but the TRE then gets handled by pynitf). The RSM
   and camera sort of fall into this category- these are geocal objects
   so geocal adds the extension to the pyntif library to support these
   types. pyntif has hooks that the user can use for adding stuff.

#. Things that don’t fall into these categories get read/written by
   the downstream users of the library.

The library is continuing to evolve. When there is something that needs to be
added to the the nitf file, there are  4 categories:

#. Stuff that really is just end user values that should be set by the
   user of pynitf. Over time, this should be the bulk of things
   read/written. So we just write project specific code to set these
   values.

#. Stuff that is already handled by pynitf. Nothing needs to be done
   other than knowing that you shouldn’t handle this downstream from the
   library.

#. Stuff that *should* be handled by pynitf but isn’t currently. This
   should get added by updating pynitf.

#. Stuff that *should* be handled by pynitf but shouldn’t actually go
   into a general purpose library. So this would be things like project
   specific TREs or objects (e.g., geocal Camera). These should get added
   by putting in extensions to pynitf, but then having them handled by
   pynitf.


On demand data
==============

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

See the class NitfImageWriteDataOnDemand, and derived classes for an example
of supplying the data on demand.

In addition, it can be useful to create TRE metadata and/or make other
changes when a NITF element is getting written out or read in. We
supply a list of "hooks" to be be run, providing a higher level interface.
See for example geocal_nitf_rsm.py in GeoCal for an example of supplying
a "rsm" object tied to the multiple RSM TREs.

The hooks are there as a convenience, there is also nothing wrong with
directly creating TREs and adding to the various segments directly.

