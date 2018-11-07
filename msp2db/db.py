#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals, print_function
import sqlite3
import sys

def create_db(file_pth=None, db_type='sqlite', db_name=None, user='', password='', schema="mona"):
    print("CREATE DB")
    if db_type == 'sqlite':
        conn = sqlite3.connect(file_pth)
        c = conn.cursor()

        c.execute('DROP TABLE IF EXISTS library_spectra_source')
        c.execute('''CREATE TABLE library_spectra_source (
                              id integer PRIMARY KEY,
                              name text NOT NULL
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


def get_connection(db_type, db_pth, user, password, name):
    if db_type == 'sqlite':
        print(db_pth)
        conn = sqlite3.connect(db_pth)
    elif db_type == 'mysql':
        import mysql.connector
        conn = mysql.connector.connect(user=user, password=password, database=name)
    elif db_type == 'django_mysql':
        from django.db import connection as conn

    return conn


def db_dict(c):
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


def chunk_query(l, n, cn, conn, name, db_type):
    # For item i in a range that is a length of l,
    [insert_query_m(l[i:i + n], name, conn, cn, db_type) for i in range(0, len(l), n)]


def insert_query_m(data, table, conn, columns=None, db_type='mysql'):

    if len(data) > 10000:
        chunk_query(data, 10000, columns, conn, table, db_type)
    else:
        if db_type == 'sqlite':
            type_sign = '?'
        else:
            type_sign = '%s'
        type_com = type_sign + ", "


        type = type_com * (len(data[0]) - 1)
        type = type + type_sign

        if columns:
            stmt = "INSERT INTO " + table + "( " + columns + ") VALUES (" + type + ")"
        else:
            stmt = "INSERT INTO " + table + " VALUES (" + type + ")"



        cursor = conn.cursor()
        cursor.executemany(stmt, data)
        conn.commit()


def make_sql_compatible(ll):
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