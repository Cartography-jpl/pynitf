from setuptools import setup

# Version moved to pynitf/version.py so we have one place it is defined.
exec(open("pynitf/version.py").read())

setup(name='pynitf',
      version=__version__,
      description='This is a package for reading and writing NITF',
      url='https://github.jpl.nasa.gov/Cartography/pynitf',
      author='Mike Smyth <Mike.M.Smyth@jpl.nasa.gov>, Philip Yoon <Philip.J.Yoon@jpl.nasa.gov>',
      author_email='Mike.M.Smyth@jpl.nasa.gov',
      license='Copyright 2020, California Institute of Technology. ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.',
      packages=['pynitf'],
      scripts=["bin/nitf_diff", "bin/nitf_info",
               "bin/explore_nitf"],
      install_requires=[
          'numpy',
          'docopt'
      ],
      setup_requires=["pytest-runner",],
      tests_requires=["pytest","h5py"],
      zip_safe=False)
