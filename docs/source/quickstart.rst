Quick start
========================================


Installation
------------
::

    $ pip install msp2db

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


