#!/usr/bin/python
# -*- coding: utf-8 -*-
import setuptools
import sys
import msp2db


def main():

    setuptools.setup(name="msp2db",
        version=msp2db.__version__,
        description="Python package for converting msp to database",
        long_description=open('README.rst').read(),
        author="Thomas N. Lawson",
        author_email="t.n.lawson@bham.ac.uk",
        url="https://github.com/computational-metabolomics/msp2db",
        license="GPLv3",
        platforms=['Windows, UNIX'],
        keywords=['Metabolomics', 'Lipidomics', 'Mass spectrometry', 'Data Processing', 'Fragmentation'],
        packages=setuptools.find_packages(),
        test_suite='tests.suite',
        install_requires=open('requirements.txt').read().splitlines(),
        include_package_data=True,
        classifiers=[
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.6",
          "Topic :: Scientific/Engineering :: Bio-Informatics",
          "Topic :: Scientific/Engineering :: Chemistry",
          "Topic :: Utilities",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Operating System :: OS Independent",
        ],
        entry_points={
         'console_scripts': [
             'msp2db = msp2db.__main__:main'
         ]
        }
    )


if __name__ == "__main__":
    main()
