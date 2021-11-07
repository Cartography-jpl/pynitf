****************************************************
NITF Special Format Changes
****************************************************

Introduction
============

One of the common issues with NITF is the need to do special formatting
for a particular field.

#. There is a formatting for a field that pynitf isn't doing correctly
   (e.g., what amounts to a bug in pynitf)
#. A particular format is needed by a partner that we are
   sending files to. In some cases this can just be because they have a 
   tool that has a more restrictive formatting assumption than the standard
   (e.g.,
   it *requires* a '+' before a positive number even if the NITF standard
   documentation doesn't), or the tool might requires a format that is actually
   wrong (e.g., what amounts to a bug in the tool they are using, but where
   the tool isn't going to be updated and we need to conform to the wrong
   format)

One of the advantages of python is that it is a dynamic language. All the
NITF handling can be changed at run time.

Note that often you need to modify the writing of a NITF field, but not
do anything special for the reading. Many of our field handlers just use
the normal python conversions (e.g., 'float()' to get a float), which doesn't
assume much about the format. So if we modify a field to a "+10.0" or a
" 10.0" or a "10.0" all get parsed when reading without change.

However in some cases you do need to update the reading also.

In the case of (1), this should ultimately get fixed in pynitf - a
bug report should be submitted and pynitf changed. But even in that case
it can useful to dynamically fix this in a particular program until a
new version of pynitf is available. So a useful procedure is to fix it
first in your application, report the problem to pynitf, and then when
you update to new version of pynitf remove your local fix.

Examples of format changes
==========================

To illustrate how to do special format changes, we'll go through a
series of examples ordered by increasing complexity.

Example 1: No change
--------------------

The first example is the base example without any change. We'll use
the TRE USE00A. There is nothing special about this TRE, it
is just a particularly simple TRE that we often use for examples. We'll
focus on one particular field "OBL_ANG" in these examples.

A basic creation/reading of this TRE is::

    from pynitf import *

    f = NitfFile()
    # Create an image segment
    t = TreUSE00A()
    t.angle_to_north = 270
    # ... Set all the other fields
    t.obl_ang = 1.0
    f.image_segment[0].tre_list.append(t)
    f.write("test.ntf")
    f2 = NitfFile("test.ntf")
    t2 = f2.image_segment[0].tre_list[0]

Most of the time when accessing a field in the TRE "t2" we are reading, we
want the data interpreted as a data type. This is the normal access attributes
that we have in the Tre class in pynitf. So for example "t2.obl_ang" will
return the floating point number 1.0. However for some purposes you want to
know exactly the string the data get represented as in the TRE. There is a
special function "get_raw_bytes" that does exactly this::

   print(t2.get_raw_bytes("obl_ang"))
   # Prints b"01.00"

Example 2: Using NitfLiteral
----------------------------

Our partner `Yoyodyne <https://en.wikipedia.org/wiki/Yoyodyne>`_ insists
that we supply this number with leading spaces (instead of 0), and with only
1 digit after the decimal place.

The easiest way to do this as a one off (e.g., something quick and dirty for
test data) is to pass a 'NitfLiteral'. This is a special class in pynitf
used to say "use this exact string". The string is padded to be the right
size for the NITF file (using python ljust to add trailing spaces), but is
otherwise unchanged.

So our example code would be::

   # ... rest of code like before
   t.obl_ang = NitfLiteral(b"  1.0")
   # ... rest of code like before
   print(t2.get_raw_bytes("obl_ang"))
   # Prints b"  1.0"

Example 3: Using a new TRE class
--------------------------------

After supplying the test file to Yoyodyne, we determine that we want to
be able to produce a number of files with this new format. We want to
modify the TRE in our local application to use the new format for all files.

Note this is also very similar to the use case of having a bug fix against
pynitf (e.g. Yoyodyne's format matches the standard and pynitf doesn't).
We may need to handle things locally until pynitf is updated, or perhaps
we have a set of changes we want to work out/batch together before modifying
pynitf.

The way to do this is to modify how pynitf handles the TRE. All the
TREs are handled by classes registered in tre_tag_to_cls (a
instance of TreTagToCls). You can either create an entirely new TRE class,
or just copy and modify the existing class.

Most of the TREs in pynitf are instances of the Tre class, which is
in turn an instance of :ref:`field-struct-section` that has the class specified
as a "desc" table. This *isn't* required, you just need to supply
the same functions as Tre has, or you can supply a
tre_implementation_class. But for this example we make a class
derived from the Tre.

Since we are only changing one field, we start with the existing
TreUSE00A desc table. An alternative is just to create an entirely
new table::

    my_desc = copy.deepcopy(TreUSE00A.desc)
    ind = [i for i,d in enumerate(my_desc) if d[0] == "obl_ang"][0]
    my_desc[ind] = ["obl_ang", "Obliquity Angle", 5, float,
                    # frmt was "%05.2lf" for 2 digits after decimal point,
                    # 0 filled on left. Change to 1 digit, space filled.
                    {"frmt" : "%5.1lf", "optional" :True}]
    class MyTreUSE00A(Tre):
        __doc__ = TreUSE00A.__doc__
        desc = my_desc
        tre_tag = TreUSE00A.tre_tag
    tre_tag_to_cls.add_cls(MyTreUSE00A)

Our example is now::

   # ... rest of code like before
   t = MyTreUSE00A()
   t.obl_ang = 1.0
   # ... rest of code like before
   print(t2.get_raw_bytes("obl_ang"))
   # Prints b"  1.0"
  
Example 4: Using a format function
----------------------------------

Sometimes a format is complicated enough it can't be captured with with
a format string.

After supplying more test data, Yoyodyne informs us that the "real" rule
they need is that they want a float with 2 digits after the decimal point
zero filled, unless the number is > 20 in which case it needs to use 1 digit
and be space filled.

The basic structure for this example is like the previous example except
we supply a formatting function instead of a format string::

    def my_format(v):
        if(v > 20):
            return "%5.1lf" % v
        return "%05.2lf" %v
    my_desc = copy.deepcopy(TreUSE00A.desc)
    ind = [i for i,d in enumerate(my_desc) if d[0] == "obl_ang"][0]
    my_desc[ind] = ["obl_ang", "Obliquity Angle", 5, float,
                    {"frmt" : my_format, "optional" :True}]
    class MyTreUSE00A(Tre):
        __doc__ = TreUSE00A.__doc__
        desc = my_desc
        tre_tag = TreUSE00A.tre_tag
    tre_tag_to_cls.add_cls(MyTreUSE00A)

If we now test on a new file::

   # ... rest of code like before
   t = MyTreUSE00A()
   t.obl_ang = 1.0
   # ... rest of code like before
   print(t2.get_raw_bytes("obl_ang"))
   # Prints b"01.00"

   # ... rest of code like before
   t = MyTreUSE00A()
   t.obl_ang = 30.0
   # ... rest of code like before
   print(t2.get_raw_bytes("obl_ang"))
   # Prints b" 30.0"

Example 5: Using a FieldData class
----------------------------------

Even more complicated, there can be formats that can't use the
normal format string for writing nor the standard python types for reading.

Yoyodyne has decided that what it really needs is the number to be zero filled,
using a space, and written backwards. For example 12.0 gets written as "00 21".

The most general formatting takes a class that is derived from
FieldData (or alternatively, just provides the same interface if
deriving from it is inconvenient).

So our example would look like::

    class ReverseNumber(FieldData):
        def get_print(self, key):
            t = self[key]
            if(t is None or len(t) == 0):
                return "Not used"
            return "%f" % t

        def unpack(self, key, v):
            return float(v.replace(b" ", b".")[::-1])
        
        def pack(self, key, v):
            return (b"%05.2f" % v).replace(b".",b" ")[::-1]

    my_desc = copy.deepcopy(TreUSE00A.desc)
    ind = [i for i,d in enumerate(my_desc) if d[0] == "obl_ang"][0]
    my_desc[ind] = ["obl_ang", "Obliquity Angle", 5, float,
                    {"field_value_class" : ReverseNumber, "optional" :True,
                     "size_not_updated" : True }]
    class MyTreUSE00A(Tre):
        __doc__ = TreUSE00A.__doc__
        desc = my_desc
        tre_tag = TreUSE00A.tre_tag
    tre_tag_to_cls.add_cls(MyTreUSE00A)

We would then use this like::
  
   # ... rest of code like before
   t = MyTreUSE00A()
   t.obl_ang = 1.0
   # ... rest of code like before
   print(t2.get_raw_bytes("obl_ang"))
   # Prints b"00 10"


Example 6: Changing and RSM TRE
-------------------------------

This is actually a non-example, we just list this to prevent any confusion.
If you are using GeoCal, you can't modify the RSM TREs directly. This is really
just a limitation imposed by another design constraint.

The RSM stuff is really pretty complicated. All the TREs are handled
by C++.  Before writing an RSM out, the GeoCal code deletes all the
existing RSM TREs and recreates them from scratch. So any changes made
to the TREs in python wouldn't stick. This is required because the set
of TREs actually depends on the RSM. I have not been able to come up
with a design that avoids this, it just seems like an inherent
complication.  Note that you *can* interact with the GeoCal Rsm C++ class
through python, but the final writing and reading of the TREs is handled by
the Rsm C++ class.

This means that changes to the RSM need to be made at the C++ level in GeoCal,
you can't play the same sorts of games like you can with all the other TREs.
This is unlike any other part of the NITF file, which gets handled by python.
Even the GLAS/GFM interface is simpler than the RSM in this regard - you can
do the same sort of modification games with the GLAS/GFM interface.
   
Full unit test examples
=======================

There is actual working pytest unit tests available in
tests/sample_format_test.py that illustrate the various modification tests.

The source is here for reference, but you can directly view and run this
in the pynitf source tree.

.. literalinclude:: ../tests/sample_format_test.py
   :caption: tests/sample_format_test.py
   :name: sample_format_test
