#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals, print_function
import sqlite3
import sys

def create_db(file_pth):
    """ Create an empty SQLite database for library spectra.

    Example:
        >>> from msp2db.db import create_db
        >>> db_pth = 'library.db'
        >>> create_db(file_pth=db_pth)

    Args:
        file_pth (str): File path for SQLite database

    """
    conn = sqlite3.connect(file_pth)
    c = conn.cursor()

    c.execute('DROP TABLE IF EXISTS library_spectra_source')
    c.execute('''CREATE TABLE library_spectra_source (
                          id integer PRIMARY KEY,
                          name text NOT NULL,
                          created_at date,
                          parsing_software text
                          )'''
              )

    c.execute('DROP TABLE IF EXISTS metab_compound')
    c.execute('''CREATE TABLE metab_compound (
                  inchikey_id text PRIMARY KEY,
                  name text,
                  pubchem_id text,
                  chemspider_id text,
                  other_names text,
                  exact_mass real,
                  molecular_formula text,
                  molecular_weight real,
                  compound_class text,
                  smiles text,
                  created_at date,
                  updated_at date

                                           )''')

    c.execute('DROP TABLE IF EXISTS library_spectra_meta')
    c.execute('''CREATE TABLE library_spectra_meta (
                                   id integer PRIMARY KEY,
                                   name text,
                                   collision_energy text,
                                   ms_level real,
                                   accession text NOT NULL,
                                   resolution text,
                                   polarity integer,
                                   fragmentation_type text,
                                   precursor_mz real,
                                   precursor_type text,
                                   instrument_type text,
                                   instrument text,
                                   copyright text,
                                   column text,
                                   mass_accuracy real,
                                   mass_error real,
                                   origin text,
                                   splash text,
                                   retention_index real, 
                                   retention_time real,
                                   library_spectra_source_id integer NOT NULL,
                                   inchikey_id text NOT NULL,
                                   FOREIGN KEY(library_spectra_source_id) REFERENCES library_spectra_source(id),
                                   FOREIGN KEY(inchikey_id) REFERENCES metab_compound(inchikey_id)
                                   )'''
              )

    c.execute('DROP TABLE IF EXISTS library_spectra')
    c.execute('''CREATE TABLE library_spectra (
                                          id integer PRIMARY KEY,
                                          mz real NOT NULL,
                                          i real NOT NULL,
                                          other text,
                                          library_spectra_meta_id integer NOT NULL,
                                          FOREIGN KEY (library_spectra_meta_id) REFERENCES library_spectra_meta(id)
                                          )'''
              )

    c.execute('DROP TABLE IF EXISTS library_spectra_annotation')
    c.execute('''CREATE TABLE library_spectra_annotation (
                                          id integer PRIMARY KEY,
                                          mz real,
                                          tentative_formula text,
                                          mass_error real,
                                          library_spectra_meta_id integer NOT NULL,
                                          FOREIGN KEY (library_spectra_meta_id) REFERENCES library_spectra_meta(id)
                                          )'''
              )


def get_connection(db_type, db_pth, user=None, password=None, name=None):
    """ Get a connection to a SQL database. Can be used for SQLite, MySQL or Django MySQL database

    Example:
        >>> from msp2db.db import get_connection
        >>> conn = get_connection('sqlite', 'library.db')

    If using "mysql" mysql.connector needs to be installed.

    If using "django_mysql" Django needs to be installed.

    Args:
        db_type (str): Type of database can either be "sqlite", "mysql" or "django_mysql"


    Returns:
       sql connection object

    """
    if db_type == 'sqlite':
        print(db_pth)
        conn = sqlite3.connect(db_pth)
    elif db_type == 'mysql':
        import mysql.connector
        conn = mysql.connector.connect(user=user, password=password, database=name)
    elif db_type == 'django_mysql':
        from django.db import connection as conn
    else:
        print('unsupported database type: {}, choices are "sqlite", "mysql" or "django_mysql"'.format(db_type))

    return conn


def db_dict(c):
    """ Get a dictionary of the library spectra from a database

    Example:
        >>> from msp2db.db import get_connection
        >>> conn = get_connection('sqlite', 'library.db')
        >>> test_db_d = db_dict(conn.cursor())

    If using a large database the resulting dictionary will be very large!

    Args:
        c (cursor): SQL database connection cursor

    Returns:
       A dictionary with the following keys 'library_spectra', 'library_spectra_meta', 'library_spectra_annotations',
       'library_spectra_source' and 'metab_compound'. Where corresponding values for each key are list of list containing
       all the rows in the database.

    """
    db_d = {}
    c.execute('SELECT * FROM library_spectra')
    db_d['library_spectra'] = [list(row) for row in c]

    c.execute('SELECT * FROM library_spectra_meta')
    db_d['library_spectra_meta'] = [list(row) for row in c]

    c.execute('SELECT * FROM library_spectra_annotation')
    db_d['library_spectra_annotations'] = [list(row) for row in c]

    c.execute('SELECT * FROM library_spectra_source')
    db_d['library_spectra_source'] = [list(row) for row in c]

    c.execute('SELECT * FROM metab_compound')
    db_d['metab_compound'] = [list(row) for row in c]

    return db_d


def insert_query_m(data, table, conn, columns=None, db_type='mysql'):
    """ Insert python list of tuples into SQL table

    Args:
        data (list): List of tuples
        table (str): Name of database table
        conn (connection object): database connection object
        columns (str): String of column names to use if not assigned then all columns are presumed to be used [Optional]
        db_type (str): If "sqlite" or "mysql"

    """
    # if length of data is very large we need to break into chunks the insert_query_m is then used recursively untill
    # all data has been inserted
    if len(data) > 10000:
        _chunk_query(data, 10000, columns, conn, table, db_type)
    else:
        # sqlite and mysql have type string (? or %s) reference to use
        if db_type == 'sqlite':
            type_sign = '?'
        else:
            type_sign = '%s'
        # create a string of types for the insertion string (e.g. ?,?,? if inserting 3 columns of data)
        type_com = type_sign + ", "
        type = type_com * (len(data[0]) - 1)
        type = type + type_sign

        # if using specific columns to insert data
        if columns:
            stmt = "INSERT INTO " + table + "( " + columns + ") VALUES (" + type + ")"
        else:
            stmt = "INSERT INTO " + table + " VALUES (" + type + ")"

        # execute query
        cursor = conn.cursor()
        cursor.executemany(stmt, data)
        conn.commit()

def _chunk_query(l, n, cn, conn, table, db_type):
    """ Call for inserting SQL query in chunks based on n rows

    Args:
        l (list): List of tuples
        n (int): Number of rows
        cn (str): Column names
        conn (connection object): Database connection object
        table (str): Table name
        db_type (str): If "sqlite" or "mysql"

    """
    # For item i in a range that is a length of l,
    [insert_query_m(l[i:i + n], table, conn, cn, db_type) for i in range(0, len(l), n)]


def _make_sql_compatible(ll):
    """ Convert any python list of lists (or tuples) so that the strings are formatted correctly for insertion into

    Args:
        ll (list): List of lists (or tuples)
    """

    new_ll = []
    for l in ll:
        new_l = ()
        for i in l:
            if not i:
                new_l = new_l + (None,)
            else:

                if isinstance(i, str):
                    if sys.version_info < (3, 0):

                        val = i.decode('utf8').encode('ascii', errors='ignore')
                    else:
                        # in py3 strings should be ok...
                        val = i
                else:
                    val = i
                new_l = new_l + (val,)
        new_ll.append(new_l)

    return new_ll