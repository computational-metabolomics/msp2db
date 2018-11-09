Quick start
========================================


Installation
------------
::

    $ pip install msp2db

Command line
------------
::

    $ msp2db -msp_pth [msp file or directory of msp files] -name [name of database] -source [name of source of msp e.g. massbank] -o [out dir]
    $ msp2db --help

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
