from setuptools import setup

setup(name='pynitf',
      version='0.61',
      description='This is a package for reading and writing NITF',
      url='https://github.jpl.nasa.gov/Cartography/pynitf',
      author='Mike Smyth <Mike.M.Smyth@jpl.nasa.gov>, Philip Yoon <Philip.J.Yoon@jpl.nasa.gov>',
      author_email='Mike.M.Smyth@jpl.nasa.gov',
      license='Copyright 2019, California Institute of Technology. ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.',
      packages=['pynitf'],
      scripts=["extra/nitf_diff", "extra/nitfinfofull",
               "extra/explore_nitf.py"],
      install_requires=[
          'six',
          'numpy',
          'docopt'
      ],
      setup_requires=["pytest-runner",],
      tests_requires=["pytest","h5py"],
      zip_safe=False)
