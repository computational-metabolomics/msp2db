# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import unittest
import sqlite3
from msp2db.parse import LibraryData
from msp2db.db import create_db, db_dict

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


def remove_date_from_metab_compound_d(d):

    for i in range(0, len(d['metab_compound'])):
        d['metab_compound'][i][10] = None
        d['metab_compound'][i][11] = None
    return d



class TestSqlite(unittest.TestCase):

    def compare_db_d(self, d1, d2):
        d1 = remove_date_from_metab_compound_d(d1)
        d2 = remove_date_from_metab_compound_d(d2)

        self.assertEquals(d1['library_spectra_annotations'], d2['library_spectra_annotations'])
        self.assertEquals(d1['metab_compound'], d2['metab_compound'])
        self.assertEquals(d1['library_spectra_meta'], d2[u'library_spectra_meta'])
        self.assertEquals(d1['library_spectra'], d2[u'library_spectra'])

    def test_create_db(self,):
        dirpath = tempfile.mkdtemp()
        # Parse all example files
        db_pth = os.path.join(os.path.dirname(__file__),
                              dirpath,
                     'test_sqlite_db_create.db')

        create_db(file_pth=db_pth)
        print(db_pth)
        conn = sqlite3.connect(db_pth)
        cursor = conn.cursor()
        # test tables exist
        self.assertTrue(check_table_exists_sqlite(cursor, 'library_spectra'))
        self.assertTrue(check_table_exists_sqlite(cursor, 'library_spectra_meta'))
        self.assertTrue(check_table_exists_sqlite(cursor, 'library_spectra_source'))
        self.assertTrue(check_table_exists_sqlite(cursor, 'metab_compound'))
        # test certain columns exit

    def test_database_dict(self):
        libdata, db_pth = self._test_example_single_file(
            os.path.join(os.path.dirname(__file__), "msp_files",  "massbank", "AC000001.txt"), 'AC')

        d_new = libdata.get_db_dict()
        d_orig = {
             u'library_spectra_annotations': [[1, 133.0643, u'C9H9O1+', -3.74, 1],
                                                   [2, 151.0751, u'C9H11O2+', -1.72, 1],
                                                   [3, 161.0591, u'C10H9O2+', -3.77, 1],
                                                   [4, 179.0702, u'C10H11O3+', -0.39, 1]],

             u'metab_compound': [[u'KWILGNNWGSNMPA-UHFFFAOYSA-N', u'Mellein', u'28516', u'26529',
                                   u'Ochracin <#> 8-hydroxy-3-methyl-3,4-dihydroisochromen-1-one', 178.06299,
                                   u'C10H10O3', None, u'Natural Product; Fungal metabolite',
                                   u'CC1CC2=C(C(=CC=C2)O)C(=O)O1', None, None]],

             u'library_spectra_meta': [[1, u'Mellein; LC-ESI-ITFT; MS2; CE: 10; R=17500; [M+H]+', u'10(NCE)',
                                        2.0, u'AC000001', u'17500', u'POSITIVE', u'HCD', 179.0697, u'[M+H]+',
                                        u'LC-ESI-ITFT', u'Q-Exactive Orbitrap Thermo Scientific',
                                        u'Copyright (C) 2017', None, None, None, None,'splash10-03fr-0900000000-035ec76d23650a15673b',
                                        None, 3.44, 1,
                                        u'KWILGNNWGSNMPA-UHFFFAOYSA-N']],

             u'library_spectra_source': [[1, u'test']],

             u'library_spectra': [[1, 133.0648, 21905.33203125, u'', 1],
                                  [2, 151.0754, 9239.8974609375, u'', 1],
                                  [3, 155.9743, 10980.8896484375, u'', 1],
                                  [4, 161.0597, 96508.4375, u'', 1],
                                  [5, 179.0703, 72563.875, u'', 1]]
        }

        d_new = remove_date_from_metab_compound_d(d_new)

        self.assertEquals(d_new['library_spectra_annotations'], d_orig['library_spectra_annotations'])
        self.assertEquals(d_new['metab_compound'], d_orig['metab_compound'])
        self.assertEquals(d_new['library_spectra_meta'], d_orig[u'library_spectra_meta'])
        self.assertEquals(d_new['library_spectra'], d_orig[u'library_spectra'])




    def _test_example_single_file(self, example_file_pth, name):
        # Parse all example files
        dirpath = tempfile.mkdtemp()
        db_pth = os.path.join(dirpath, name + '.db')

        create_db(file_pth=db_pth)

        libdata = LibraryData(msp_pth=example_file_pth, db_pth=db_pth, db_type="sqlite",
                              schema='massbank',
                              source='test',
                              mslevel=None,
                              chunk=200)
        return libdata, db_pth

    def test_example_single_file_massbank_AC(self):

        libdata, db_pth = self._test_example_single_file(
            os.path.join(os.path.dirname(__file__), "msp_files",  "massbank", "AC000001.txt"), 'AC')

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
        # dirpath = os.path.join(os.path.dirname(__file__), 'original_results')
        db_pth = os.path.join(dirpath, 'test_msp_dir.db')

        create_db(file_pth=db_pth)

        dir_pth = os.path.join(os.path.dirname(__file__), "msp_files", "massbank")

        libdata = LibraryData(msp_pth=dir_pth,
                              db_pth=db_pth,
                              db_type='sqlite',

                              schema='massbank',
                              source='test',
                              mslevel=None,
                              chunk=200)

        db_new = libdata.get_db_dict()

        # get original database info
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'original_results', 'test_msp_dir.db'))
        cursor = conn.cursor()

        db_original = db_dict(cursor)

        self.compare_db_d(db_new, db_original)


    def test_mona_files(self):
        self.maxDiff = None

        dirpath = tempfile.mkdtemp()
        # dirpath = os.path.join(os.path.dirname(__file__), 'original_results')
        db_pth = os.path.join(dirpath, 'test_msp_mona.db')

        create_db(file_pth=db_pth)

        libdata = LibraryData(msp_pth=os.path.join(os.path.dirname(__file__), 'msp_files', 'mona', 'MoNA-export-Pathogen_Box-small.msp'),
                              db_pth=db_pth,
                              db_type='sqlite',

                              schema='mona',
                              source='pathogen',
                              mslevel=None,
                              chunk=2)

        libdata = LibraryData(msp_pth=os.path.join(os.path.dirname(__file__), 'msp_files', 'mona', 'MoNA-export-MetaboBASE-small.msp'),

                              db_pth=db_pth,
                              db_type='sqlite',

                              schema='mona',
                              source='massbank',
                              mslevel=None,
                              chunk=2)

        libdata = LibraryData(msp_pth=os.path.join(os.path.dirname(__file__), 'msp_files', 'mona', 'MoNA-export-MassBank-small.msp'),
                              db_pth=db_pth,
                              db_type='sqlite',

                              schema='mona',
                              source='metabobase',
                              mslevel=None,
                              chunk=2)

        db_new = libdata.get_db_dict()

        # get original database info
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'original_results', 'test_msp_mona.db'))
        cursor = conn.cursor()

        db_original = db_dict(cursor)

        self.compare_db_d(db_new, db_original)


class TestCLI(unittest.TestCase):

    def compare_db_d(self, d1, d2):
        d1 = remove_date_from_metab_compound_d(d1)
        d2 = remove_date_from_metab_compound_d(d2)

        self.assertEquals(d1['library_spectra_annotations'], d2['library_spectra_annotations'])
        self.assertEquals(d1['metab_compound'], d2['metab_compound'])
        self.assertEquals(d1['library_spectra_meta'], d2[u'library_spectra_meta'])
        self.assertEquals(d1['library_spectra'], d2[u'library_spectra'])

    def test_cli(self,):

        dirpath = tempfile.mkdtemp()
        # dirpath = os.path.join(os.path.dirname(__file__), 'original_results')

        infile = os.path.join(os.path.dirname(__file__), 'msp_files',  "massbank", "AC000001.txt")
        call = "msp2db --msp_pth {} --source massbank -o {} -t sqlite --schema massbank".format(infile, os.path.join(dirpath, 'test_sqlite_cli.db'))
        print(call)
        os.system(call)

        db_pth = os.path.join(dirpath, 'test_sqlite_cli.db')

        # get original database info
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'original_results', 'test_sqlite_cli.db'))
        cursor = conn.cursor()
        db_original = db_dict(cursor)

        conn2 = sqlite3.connect(db_pth)
        cursor2 = conn2.cursor()
        db_new = db_dict(cursor2)

        self.compare_db_d(db_new, db_original)


