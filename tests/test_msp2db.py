# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import unittest
import sqlite3
from msp2db.msp2db import LibraryData, create_db

from sqlite3 import OperationalError
import tempfile
import shutil



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
        dirpath = tempfile.mkdtemp()
        # Parse all example files
        db_pth = os.path.join(os.path.dirname(__file__),
                              dirpath,
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
        dirpath = tempfile.mkdtemp()
        db_pth = os.path.join(os.path.dirname(__file__),
                              dirpath, name + '.db')

        create_db(file_pth=db_pth, db_type='sqlite', db_name=name)

        libdata = LibraryData(msp_pth=example_file_pth,

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

        for row in cursor:
            print(row)
            self.assertEquals(row[names['name']], 'Mellein; LC-ESI-ITFT; MS2; CE: 10; R=17500; [M+H]+')
            self.assertEquals(row[names['collision_energy']], '10(NCE)')
            self.assertEquals(row[names['ms_level']], 2)
            self.assertEquals(row[names['accession']], 'AC000001')
            self.assertEquals(row[names['resolution']], '17500')
            self.assertEquals(row[names['polarity']], 'POSITIVE')
            self.assertEquals(row[names['fragmentation_type']], 'HCD')
            self.assertEquals(row[names['precursor_mz']], 179.0697)
            self.assertEquals(row[names['precursor_type']], '[M+H]+')
            self.assertEquals(row[names['instrument_type']], 'LC-ESI-ITFT')
            self.assertEquals(row[names['instrument']],'Q-Exactive Orbitrap Thermo Scientific')
            self.assertEquals(row[names['copyright']], 'Copyright (C) 2017')
            self.assertEquals(row[names['inchikey_id']], 'KWILGNNWGSNMPA-UHFFFAOYSA-N')

        qry = cursor.execute("SELECT * FROM metab_compound")
        names = sql_column_names(qry)

        for row in cursor:
            print(row)
            self.assertEquals(row[names['inchikey_id']], 'KWILGNNWGSNMPA-UHFFFAOYSA-N')
            self.assertEquals(row[names['name']], 'Mellein')
            self.assertEquals(row[names['pubchem_id']], '28516')
            self.assertEquals(row[names['chemspider_id']], '26529')
            self.assertEquals(row[names['other_names']], 'Ochracin <#> 8-hydroxy-3-methyl-3,4-dihydroisochromen-1-one')
            self.assertEquals(row[names['exact_mass']], 178.06299)
            self.assertEquals(row[names['molecular_formula']], 'C10H10O3')
            self.assertEquals(row[names['compound_class']], 'Natural Product; Fungal metabolite')
            self.assertEquals(row[names['smiles']], 'CC1CC2=C(C(=CC=C2)O)C(=O)O1')

        qry = cursor.execute("SELECT * FROM library_spectra_source")
        names = sql_column_names(qry)

        for row in cursor:
            print(row)
            self.assertEquals(row[names['name']], 'test')

        qry = cursor.execute("SELECT * FROM library_spectra")
        names = sql_column_names(qry)
        peaks_to_test = []
        for row in cursor:
            peaks_to_test.append(list(row))

        peaks = [[1, 133.0648, 21905.33203125, '', 1],
                 [2, 151.0754, 9239.8974609375, '', 1],
                 [3, 155.9743, 10980.8896484375, '', 1],
                 [4, 161.0597, 96508.4375, '', 1],
                 [5, 179.0703, 72563.875, '', 1]]

        self.assertEquals(peaks_to_test, peaks)

    def test_example_multi_file(self):

        dirpath = tempfile.mkdtemp()
        db_pth = os.path.join(os.path.dirname(__file__),
                              dirpath, 'test_msp_dir.db')

        create_db(file_pth=db_pth, db_type='sqlite', db_name='test_dir')

        dir_pth = os.path.join(os.path.dirname(__file__), "msp_files")

        libdata = LibraryData(msp_pth=dir_pth,

                              db_pth=db_pth,
                              db_type='sqlite',
                              d_form=None,
                              schema='massbank',
                              source='test',
                              mslevel=None,
                              chunk=200)


    def test_mona_files(self):

        dirpath = tempfile.mkdtemp()
        db_pth = os.path.join(os.path.dirname(__file__),
                              dirpath, 'test_msp_dir.db')

        create_db(file_pth=db_pth, db_type='sqlite', db_name='test_mona')

        libdata = LibraryData(msp_pth=os.path.join(os.path.dirname(__file__), 'msp_files', 'mona', 'MoNA-export-Pathogen_Box-small.msp'),
                              db_pth=db_pth,
                              db_type='sqlite',
                              d_form=None,
                              schema='mona',
                              source='pathogen',
                              mslevel=None,
                              chunk=200)

        libdata = LibraryData(msp_pth=os.path.join(os.path.dirname(__file__), 'msp_files', 'mona', 'MoNA-export-MetaboBASE-small.msp'),

                              db_pth=db_pth,
                              db_type='sqlite',
                              d_form=None,
                              schema='mona',
                              source='massbank',
                              mslevel=None,
                              chunk=200)

        libdata = LibraryData(msp_pth=os.path.join(os.path.dirname(__file__), 'msp_files', 'mona', 'MoNA-export-MassBank-small.msp'),
                              db_pth=db_pth,
                              db_type='sqlite',
                              d_form=None,
                              schema='mona',
                              source='metabobase',
                              mslevel=None,
                              chunk=200)





