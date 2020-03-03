****************************************************
Introduction
****************************************************

This library is used for reading and writing NITF format files.

The overall NITF file specification is described in `MIL-STD-2500C <https://gwg.nga.mil/ntb/baseline/docs/2500c/2500C.pdf>`_.

Many of the TREs are described in `STDI-0002-1_4.0 <https://nsgreg.nga.mil/NSGDOC/files/doc/Document/STDI_0002_1_4.zip>`_.

Additional documentation available at `Reference Library for NITFS Users <https://www.gwg.nga.mil/ntb/baseline/format.html>`_.

Install
=======

This has standard setup.py. You can install a tar file using pip, or
run setup tools directly (e.g., python setup.py install).

As a convenience, there is also a Makefile, you can build with::

    make install

Testing
=======

Tests can be run by::

    python setup.py test
	
Standard pytest arguments can be passed::

    python setup.py test --addopts="-k test_tre_read"

For development, it can be useful to run just a single file. You can 
do this by::

    PYTHONPATH=`pwd`:${PYTHONPATH} pytest -s tests/nitf_tre_test.py

Like with install, there is a Makefile for convenience::

    make check

Build documentation
===================

The documentation is available online. You only did to build the documentation
if you are updating it, or want the documentation in another format.

To build the documentation, you need a few extra packages

* sphinx
* PlantUML (see `PlantUML <http://plantuml.com/>`_)
* sphinxcontrib-plantuml (see `sphinxcontrib-plantuml <https://pypi.org/project/sphinxcontrib-plantuml/>`_)
* ghp-import2 (see `ghp-import2 <https://pypi.org/project/ghp-import2/>`_)

You can run sphix directly, or use the Makefile::

   make doc-html
   make doc-latex
   make doc-latexpdf

Note that if you update the HTML, you will generally want to upload this to
the github page. This can be done using ghp-import, or with the Makefile::

   make github-pages

Creating package
================

Quick command to create a tar file including version number. First, make sure
the version number is setup.py is correct. Then do something like::

    V=`grep __version__ pynitf/version.py | sed -r 's/.*"(.*)".*/\1/'`
    git tag -s $V -m "This is my new version"
    git push origin $V
    git archive --format=tar --prefix=pyntif-$V/ $V | gzip --best > pynitf-$V.tar.gz

Note you can also just download the tar.gz file from github after you create
the tag, if that is easier.
