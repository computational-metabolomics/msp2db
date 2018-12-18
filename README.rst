msp2db
======

|Version| |Py versions| |Git| |Build Status (Travis)| |Build Status (AppVeyor)| |License| |RTD doc| |codecov|

Python package to create an SQLite database from a collection of MSP mass spectromertry spectra files. Currently works with MSP files formated as  `MassBank records <https://github.com/MassBank/MassBank-data>`__
or as  `MoNA records <http://mona.fiehnlab.ucdavis.edu/downloads>`__.

The resulting SQLite database can be used for spectral matching with    `msPurity Bioconductor R package <https://bioconductor.org/packages/release/bioc/html/msPurity.html>`__, see `vigenette. <https://bioconductor.org/packages/release/bioc/vignettes/msPurity/inst/doc/msPurity-spectral-matching-vignette.html>`__



Installation
------------
::

    $ pip install .

Command line
------------
::

    $ msp2db --msp_pth [msp file or directory of msp files] --source [name of source of msp e.g. massbank] -out_pth [out dir]
    $ msp2db --help

    usage: PROG [-h] -m MSP_PTH -s SOURCE [-o OUT_PTH] [-t TYPE] [-d] [-l MSLEVEL]
            [-c CHUNK] [-x SCHEMA]

    Convert msp to SQLite or MySQL database

    optional arguments:
        -h, --help            show this help message and exit
        -m MSP_PTH, --msp_pth MSP_PTH
                                path to the MSP file (or directory of msp files)
        -s SOURCE, --source SOURCE
                                Name of data source (e.g. MassBank, LipidBlast)
        -o OUT_PTH, --out_pth OUT_PTH
                                file path for SQLite database
        -t TYPE, --db_type TYPE
                                database type [mysql, sqlite]
        -d, --delete_tables   delete tables
        -l MSLEVEL, --mslevel MSLEVEL
                                ms level of fragmentation if not detailed in msp file
        -c CHUNK, --chunk CHUNK
                                Chunks of spectra to parse data (useful to control
                                memory usage)
        -x SCHEMA, --schema SCHEMA
                                Type of schema used (by default is "mona" msp style
                                but can use "massbank" style)

    --------------

API
------------
.. code-block:: python

    db_pth = 'spectral_library_07112018v1.db'
    create_db(file_pth=db_pth, db_type='sqlite', db_name='spectra')
    libdata = LibraryData(msp_pth='MoNA-export-FAHFA.msp',
                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='fahfa',
                      mslevel=None,
                      chunk=200)



Developers & Contributors
-------------------------
Tom Lawson: t.n.lawson@bham.ac.uk

License
-------
Released under the GNU General Public License v3.0 (see `LICENSE file <https://github.com/computational-metabolomics/msp2db/blob/master/LICENSE>`_)


.. |Build Status (Travis)| image:: https://img.shields.io/travis/computational-metabolomics/msp2db.svg?style=flat&maxAge=3600&label=Travis-CI
   :target: https://travis-ci.org/computational-metabolomics/msp2db

.. |Py versions| image:: https://img.shields.io/pypi/pyversions/msp2db.svg?style=flat&maxAge=3600
   :target: https://pypi.python.org/pypi/msp2db/
  
.. |Build Status (AppVeyor)| image:: https://img.shields.io/appveyor/ci/Tomnl/msp2db.svg?style=flat&maxAge=3600&label=AppVeyor
   :target: https://ci.appveyor.com/project/Tomnl/msp2db

.. |Version| image:: https://img.shields.io/pypi/v/msp2db.svg?style=flat&maxAge=3600
   :target: https://pypi.python.org/pypi/msp2db/

.. |Git| image:: https://img.shields.io/badge/repository-GitHub-blue.svg?style=flat&maxAge=3600
   :target: https://github.com/ISA-tools/msp2db


.. |License| image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg
   :target: https://www.gnu.org/licenses/gpl-3.0.html

.. |RTD doc| image:: https://img.shields.io/readthedocs/msp2db.svg?style=flat&maxAge=3600
   :target: https://msp2db.readthedocs.io/en/latest/
   
.. |codecov| image:: https://codecov.io/gh/computational-metabolomics/msp2db/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/computational-metabolomics/msp2db



