#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals, print_function
import datetime
import re
import os
import pubchempy as pcp
import uuid
import six
from .re import get_compound_regex, get_meta_regex
from .db import get_connection, insert_query_m, make_sql_compatible, db_dict
from .utils import removekey, get_precursor_mz, line_count

try:
    # For Python 3.0 and later
    from urllib.request import URLError
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import URLError

try:
    from http.client import BadStatusLine
except ImportError:
    from httplib import BadStatusLine


class LibraryData(object):
    def __init__(self, msp_pth, source, mslevel=None,
                 db_pth=None, db_type='sqlite', d_form=False, password='', user='', mysql_db_name=None,
                 chunk=0, schema = 'mona', user_meta_regex=None, user_compound_regex=None, celery_obj=False):

        conn = get_connection(db_type, db_pth, user, password, mysql_db_name)
        print('Starting library data parsing')
        self.c = conn.cursor()
        self.conn = conn
        self.db_pth = db_pth

        self.meta_info_all = []

        self.compound_info_all = []
        self.compound_ids = []
        self.get_compound_ids()

        self.spectra_all = []
        self.spectra_annotation_all = []
        self.start_spectra = False
        self.start_spectra_annotation = False
        self.ignore_additional_spectra_info = False
        self.collect_meta = True
        self.update_source = True

        if user_meta_regex:
            self.meta_regex = user_meta_regex
        else:
            self.meta_regex = get_meta_regex(schema=schema)

        if user_compound_regex:
            self.compound_regex = user_meta_regex
        else:
            self.compound_regex = get_compound_regex(schema=schema)

        self.meta_info = self.get_blank_meta_info()

        self.compound_info = self.get_blank_compound_info()
        self.get_current_ids()
        self.source = source
        self.mslevel = mslevel
        self.other_names = []

        if d_form:
            self.num_lines = sum(1 for line in msp_pth)
            self.parse_files(msp_pth,
                              chunk,
                              db_type,
                              celery_obj=celery_obj
                              )
        else:

            self.parse_files(msp_pth, chunk, db_type, celery_obj=celery_obj)

    def get_current_ids(self, source=True, meta=True, spectra=True, spectra_annotation=True):
        c = self.c
        # Get the last uid for the spectra_info table
        if source:
            c.execute('SELECT max(id) FROM library_spectra_source')
            last_id_origin = c.fetchone()[0]
            if last_id_origin:
                self.current_id_origin = last_id_origin + 1
            else:
                self.current_id_origin = 1

        if meta:
            c.execute('SELECT max(id) FROM library_spectra_meta')
            last_id_meta = c.fetchone()[0]

            if last_id_meta:
                self.current_id_meta = last_id_meta + 1
            else:
                self.current_id_meta = 1

        if spectra:
            c.execute('SELECT max(id) FROM library_spectra')
            last_id_spectra = c.fetchone()[0]

            if last_id_spectra:
                self.current_id_spectra = last_id_spectra + 1
            else:
                self.current_id_spectra = 1

        if spectra_annotation:
            c.execute('SELECT max(id) FROM library_spectra_annotation')
            last_id_spectra_annotation = c.fetchone()[0]

            if last_id_spectra_annotation:
                self.current_id_spectra_annotation = last_id_spectra_annotation + 1
            else:
                self.current_id_spectra_annotation = 1


    def parse_files(self, msp_pth, chunk, db_type, celery_obj=False):

        c = 0
        if os.path.isdir(msp_pth):
            for msp_file in sorted(os.listdir(msp_pth)):
                msp_file_pth = os.path.join(msp_pth, msp_file)
                if os.path.isdir(msp_file_pth):
                    continue
                print('MSP FILE PATH', msp_file_pth)
                self.num_lines = line_count(msp_file_pth)
                with open(msp_file_pth, "r") as f:
                    c = self.parse_lines(f, chunk, db_type, celery_obj, c)
        else:
            self.num_lines = line_count(msp_pth)
            with open(msp_pth, "r") as f:
                self.parse_lines(f, chunk, db_type, celery_obj)

        self.insert_data(remove_data=True, db_type=db_type)

    def parse_lines(self, f, chunk, db_type, celery_obj=False, c=0):
        old = 0

        for i, line in enumerate(f):
            if i == 0:
                old = self.current_id_meta

            self.update_libdata(line)

            if self.current_id_meta > old:
                old = self.current_id_meta
                c += 1

            if c > chunk:

                if celery_obj:
                    celery_obj.update_state(state='current spectra {}'.format(str(i)),
                                            meta={'current': i, 'total': self.num_lines})
                print(self.current_id_meta)
                self.insert_data(remove_data=True, db_type=db_type)
                self.update_source = False
                c = 0
        return c

    def update_libdata(self, line):

        ####################################################
        # Parse the lines
        ####################################################
        if re.match('^Comment.*$', line, re.IGNORECASE):
            comments = re.findall('"([^"]*)"', line)
            for c in comments:
                self.parse_meta_info(c)
                self.parse_compound_info(c)
        self.parse_meta_info(line)
        self.parse_compound_info(line)


        # num peaks
        if self.collect_meta and (re.match('^Num Peaks(.*)$', line, re.IGNORECASE) or re.match('^PK\$PEAK:(.*)', line,
                re.IGNORECASE) or re.match('^PK\$ANNOTATION(.*)', line, re.IGNORECASE)):

            self.store_compound_info()

            self.store_meta_info()

            # Reset the temp meta information
            self.meta_info = self.get_blank_meta_info()
            self.compound_info = self.get_blank_compound_info()
            self.other_names = []
            self.collect_meta = False

        if re.match('^PK\$PEAK: m/z int\. rel\.int\.$', line, re.IGNORECASE):
            self.ignore_additional_spectra_info = True

        if re.match('^Num Peaks(.*)$', line, re.IGNORECASE) or re.match('^PK\$PEAK:(.*)', line, re.IGNORECASE):
            self.start_spectra = True
            return
        elif re.match('^PK\$ANNOTATION(.*)', line, re.IGNORECASE):
            self.start_spectra_annotation = True
            return

        if self.start_spectra_annotation:
            self.parse_spectra_annotation(line)

        if self.start_spectra:
            self.parse_spectra(line)


    def get_compound_ids(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT inchikey_id FROM metab_compound')
        self.conn.commit()
        for row in cursor:
            if not row[0] in self.compound_ids:
                self.compound_ids.append(row[0])

    def store_compound_info(self):
        other_name_l = [name for name in self.other_names if name != self.compound_info['name']]
        self.compound_info['other_names'] = ' <#> '.join(other_name_l)

        if not self.compound_info['inchikey_id']:
            self.set_inchi_pcc(self.compound_info['pubchem_id'], 'cid', 0)

        if not self.compound_info['inchikey_id']:
            self.set_inchi_pcc(self.compound_info['smiles'], 'smiles', 0)

        if not self.compound_info['inchikey_id']:
            self.set_inchi_pcc(self.compound_info['name'], 'name', 0)

        if not self.compound_info['inchikey_id']:
            print('WARNING, cant get inchi key for ', self.compound_info)
            print(self.meta_info)
            print('#########################')
            self.compound_info['inchikey_id'] = 'UNKNOWN_' + str(uuid.uuid4())

        if not self.compound_info['pubchem_id'] and self.compound_info['inchikey_id']:
            self.set_inchi_pcc(self.compound_info['inchikey_id'], 'inchikey', 0)

        if not self.compound_info['name']:
            self.compound_info['name'] = 'unknown name'

        if not self.compound_info['inchikey_id'] in self.compound_ids:
            self.compound_info_all.append(tuple(self.compound_info.values()) + (
                str(datetime.datetime.now()),
                str(datetime.datetime.now()),
            ))
            self.compound_ids.append(self.compound_info['inchikey_id'])

    def store_meta_info(self):
        # In the mass bank msp files, sometimes the precursor_mz is missing but we have the neutral mass and
        # the precursor_type (e.g. adduct) so we can calculate the precursor_mz
        if not self.meta_info['precursor_mz'] and self.meta_info['precursor_type'] and \
                self.compound_info['exact_mass']:
            self.meta_info['precursor_mz'] = get_precursor_mz(float(self.compound_info['exact_mass']),
                                                              self.meta_info['precursor_type'])

        if not self.meta_info['polarity']:
            # have to do special check for polarity (as sometimes gets missed)
            m = re.search('^\[.*\](\-|\+)', self.meta_info['precursor_type'], re.IGNORECASE)
            if m:
                polarity = m.group(1).strip()
                if polarity == '+':
                    self.meta_info['polarity'] = 'positive'
                elif polarity == '-':
                    self.meta_info['polarity'] = 'negative'

        if not self.meta_info['accession']:
            self.meta_info['accession'] = 'unknown accession'

        self.meta_info_all.append(
            (str(self.current_id_meta),) +
            tuple(self.meta_info.values()) +
            (str(self.current_id_origin), self.compound_info['inchikey_id'],)
        )

    def parse_spectra_annotation(self, line):


        if re.match('^PK\$NUM_PEAK(.*)', line, re.IGNORECASE):
            self.start_spectra_annotation = False
            return

        saplist = line.split()
        'm/z tentative_formula mass_error'
        sarow = (
            self.current_id_spectra_annotation,
            float(saplist[0]),
            saplist[1],
            float(saplist[2]),
            self.current_id_meta)

        self.spectra_annotation_all.append(sarow)

        self.current_id_spectra_annotation += 1

    def parse_spectra(self, line):


        if line in ['\n', '\r\n', '//\n', '//\r\n']:
            self.start_spectra = False
            self.current_id_meta += 1
            self.collect_meta = True
            return

        splist = line.split()

        if len(splist) > 2 and not self.ignore_additional_spectra_info:
            additional_info = ''.join(map(str, splist[2:len(splist)]))
        else:
            additional_info = ''

        srow = (
            self.current_id_spectra, float(splist[0]), float(splist[1]), additional_info,
            self.current_id_meta)

        self.spectra_all.append(srow)

        self.current_id_spectra += 1


    def get_blank_meta_info(self):
        return {k: '' for k in self.meta_regex.keys()}

    def get_blank_compound_info(self,):
        return {k: '' for k in self.compound_regex.keys()}

    def set_inchi_pcc(self, in_str, pcp_type, elem):
        if not in_str:
            return 0

        try:
            pccs = pcp.get_compounds(in_str, pcp_type)
        except pcp.BadRequestError as e:
            print(e)
            return 0
        except pcp.TimeoutError as e:
            print(e)
            return 0
        except urllib2.URLError as e:
            print(e)
            return 0
        except BadStatusLine as e:
            print(e)
            return 0

        if pccs:
            pcc = pccs[elem]
            self.compound_info['inchikey_id'] = pcc.inchikey
            self.compound_info['pubchem_id'] = pcc.cid
            self.compound_info['molecular_formula'] = pcc.molecular_formula
            self.compound_info['molecular_weight'] = pcc.molecular_weight
            self.compound_info['exact_mass'] = pcc.exact_mass
            self.compound_info['smiles'] = pcc.canonical_smiles

            if len(pccs) > 1:
                print('WARNING, multiple compounds for ', self.compound_info)

    def get_other_names(self, line):
        m = re.search(self.compound_regex['other_names'][0], line, re.IGNORECASE)
        if m:
            self.other_names.append(m.group(1).strip())

    def parse_meta_info(self, line):
        if self.mslevel:
            self.meta_info['ms_level'] = self.mslevel

        for k, regexes in six.iteritems(self.meta_regex):
            for reg in regexes:
                m = re.search(reg, line, re.IGNORECASE)
                if m:
                    self.meta_info[k] = m.group(1).strip()

    def parse_compound_info(self, line):

        for k, regexes in six.iteritems(self.compound_regex):
            for reg in regexes:
                if self.compound_info[k]:
                    continue
                m = re.search(reg, line, re.IGNORECASE)
                if m:
                    self.compound_info[k] = m.group(1).strip()

        self.get_other_names(line)

    def insert_data(self, remove_data=False, schema='mona', db_type='sqlite'):
        print("INSERT DATA")

        if self.update_source:
            # print "insert ref id"
            self.c.execute(
                "INSERT INTO library_spectra_source (id, name) VALUES ({a}, '{b}')".format(a=self.current_id_origin,
                                                                                           b=self.source))
            self.conn.commit()

        if self.compound_info_all:
            self.compound_info_all = make_sql_compatible(self.compound_info_all)

            cn = ', '.join(self.compound_info.keys()) + ',created_at,updated_at'

            insert_query_m(self.compound_info_all, columns=cn, conn=self.conn, table='metab_compound',
                           db_type=db_type)

        self.meta_info_all = make_sql_compatible(self.meta_info_all)

        cn = 'id,' + ', '.join(self.meta_info.keys()) + ',library_spectra_source_id, inchikey_id'

        insert_query_m(self.meta_info_all, columns=cn, conn=self.conn, table='library_spectra_meta',
                       db_type=db_type)


        cn = "id, mz, i, other, library_spectra_meta_id"
        insert_query_m(self.spectra_all, columns=cn, conn=self.conn, table='library_spectra', db_type=db_type)
        if self.spectra_annotation_all:
            cn = "id, mz, tentative_formula, mass_error, library_spectra_meta_id"
            insert_query_m(self.spectra_annotation_all, columns=cn, conn=self.conn,
                           table='library_spectra_annotation', db_type=db_type)


        # self.conn.close()
        if remove_data:
            self.meta_info_all = []
            self.spectra_all = []
            self.spectra_annotation_all = []
            self.compound_info_all = []
            self.get_current_ids(source=False)

    def get_db_dict(self):
        return db_dict(self.c)

    def close(self):
        self.conn.close()
