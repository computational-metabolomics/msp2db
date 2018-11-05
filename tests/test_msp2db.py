# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import unittest
import sqlite3
from msp2db.msp2db import LibraryData, create_db

from sqlite3 import OperationalError


def check_table_exists_sqlite(cursor, tablename):
    #https://stackoverflow.com/questions/17044259/python-how-to-check-if-table-exists
    try:
        qry =cursor.execute("SELECT NULL FROM {} LIMIT 1".format(tablename))
    except OperationalError as e:
        return False

    return True


def sql_column_names(cursor):
    names = {}
    c = 0
    for description in cursor.description:
        names[description[0]] = c
        c += 1

    return names
#
class TestSqlite(unittest.TestCase):

    def test_create_db(self,):
        # Parse all example files
        db_pth = os.path.join(os.path.dirname(__file__),
                     'original_results',
                     'test_sqlite_db_create.db')

        create_db(file_pth=db_pth,
                           db_type='sqlite',
                           db_name='test')
        print(db_pth)
        conn = sqlite3.connect(db_pth)
        cursor = conn.cursor()
        # test tables exist
        self.assertTrue(check_table_exists_sqlite(cursor, 'library_spectra'))
        self.assertTrue(check_table_exists_sqlite(cursor, 'library_spectra_meta'))
        self.assertTrue(check_table_exists_sqlite(cursor, 'library_spectra_source'))
        self.assertTrue(check_table_exists_sqlite(cursor, 'metab_compound'))
        # test certain columns exit


    def _test_example_single_file(self, example_file_pth, name):
        # Parse all example files
        db_pth = os.path.join(os.path.dirname(__file__),
                     'original_results', name + '.db')

        create_db(file_pth=db_pth, db_type='sqlite', db_name=name)

        libdata = LibraryData(msp_pth=example_file_pth,
                              name=name,
                              db_pth=db_pth,
                              db_type='sqlite',
                              d_form=None,
                              schema='massbank',
                              source='test',
                              mslevel=None,
                              chunk=200)
        return libdata, db_pth

    def test_example_single_file_massbank_AC(self):

        libdata, db_pth = self._test_example_single_file(
            os.path.join(os.path.dirname(__file__), "msp_files", "AC000001.txt"), 'AC')

        conn = sqlite3.connect(db_pth)
        cursor = conn.cursor()

        qry = cursor.execute("SELECT * FROM library_spectra_meta")
        names = sql_column_names(qry)
        print(names)

        names = ['polarity', 'instrument_type','name', 'copyright', 'collision_energy','column',  'accession',
        'precursor_mz', 'fragmentation_type', 'instrument', 'library_spectra_source_id', 'ms_level', 'inchikey_id',
        'mass_error', 'mass_accuracy', 'precursor_type', 'resolution', 'id', 'origin']
        for row in cursor:
            print(row)
        print(libdata)

    def test_example_single_file_BS(self):
        libdata = self._test_example_single_file(os.path.join(os.path.dirname(__file__), "msp_files", "BS001001.txt"), 'BS')
        print(libdata)



