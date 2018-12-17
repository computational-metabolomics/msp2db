# coding: utf-8
from __future__ import absolute_import, unicode_literals, print_function
import datetime
import re
import os
import pubchempy as pcp
import csv
import uuid
import six
from .re import get_compound_regex, get_meta_regex
from .db import get_connection, insert_query_m, _make_sql_compatible, db_dict
from .utils import get_precursor_mz, line_count, get_blank_dict

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
    """MSP file parser to SQL databases

    After creating a SQL database for the library spectra using create_db, MSP files can be parsed into the database
    using the LibraryData class.

    Example:
        >>> from msp2db.db import create_db
        >>> from msp2db.parse import LibraryData
        >>> db_pth = 'spectral_library.db'
        >>> create_db(file_pth=db_pth, db_type='sqlite', db_name='spectra')
        >>> libdata = LibraryData(msp_pth='MoNA-export-FAHFA.msp',
        >>>                  db_pth=db_pth,
        >>>                  db_type='sqlite',
        >>>                  schema='mona',
        >>>                  source='fahfa',
        >>>                  chunk=200)

    Args:
        msp_pth (str): path to msp file or directory [required]
        db_pth (str): path to sqlite database (only required when using SQLite database) [default None]
        source (str): Source of the msp files (e.g. massbank) [default 'unknown']
        mslevel (int): If the msp file does not contain the mslevel this can be defined here [default None]
        db_type (str): The type of database to submit to (either 'sqlite', 'mysql' or 'django_mysql') [default sqlite]
        user (str): Username for database (only required for non Django mysql databases) [default None]
        password (str): Password for database (only required for non Django mysql databases) [default None]
        mysql_db_name (str):  Name of the mysql database (only required for non Django mysql databases) [default None]
        chunk (int): Chunks of spectra to parse data (useful to control memory usage) [default 200]
        schema (str): MSP files can vary based on how they were made, two standard schemas are available either 'mona'
                      based on the MassBank of North America (MoNA) MSP files. And 'massbank' which is based on the
                      more controlled MassBank MSP files https://github.com/MassBank/MassBank-data [default 'mona']
        user_meta_regex (dict): For other MSP files not derived from either MoNA or MassBank a custom dictionary of
                                regexes can be used [default None]
        user_compound_regex (dict): For other MSP files not derived from either MoNA or MassBank a custom dictionary of
                                    regexes can be used [default None]
        celery_obj (boolean): If using Django a Celery task object can be used to keep track on ongoing tasks
                              [default False]

    Returns:
        LibraryData object
    """
    def __init__(self, msp_pth, db_pth=None,
                 mslevel=None, source='unknown', db_type='sqlite', password=None, user=None,
                 mysql_db_name=None, chunk=200, schema='mona', user_meta_regex=None, user_compound_regex=None,
                 celery_obj=False):

        # get the database connection (either sqlite, mysql or Django mysql)
        conn = get_connection(db_type, db_pth, user, password, mysql_db_name)

        # set up object variables
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
        self.source = source
        self.mslevel = mslevel
        self.other_names = []

        # Either get standard regexs or the user provided regexes
        if user_meta_regex:
            self.meta_regex = user_meta_regex
        else:
            self.meta_regex = get_meta_regex(schema=schema)

        if user_compound_regex:
            self.compound_regex = user_meta_regex
        else:
            self.compound_regex = get_compound_regex(schema=schema)

        # initiate the meta data
        self.meta_info = get_blank_dict(self.meta_regex)
        self.compound_info = get_blank_dict(self.compound_regex)
        self._get_current_ids()

        # parse the file(s)
        self._parse_files(msp_pth, chunk, db_type, celery_obj=celery_obj)

    def _get_current_ids(self, source=True, meta=True, spectra=True, spectra_annotation=True):
        """Get the current id for each table in the database

        Args:
            source (boolean): get the id for the table "library_spectra_source" will update self.current_id_origin
            meta (boolean): get the id for the table "library_spectra_meta" will update self.current_id_meta
            spectra (boolean): get the id for the table "library_spectra" will update self.current_id_spectra
            spectra_annotation (boolean): get the id for the table "library_spectra_annotation" will update
                                          self.current_id_spectra_annotation

        """
        # get the cursor for the database connection
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


    def _parse_files(self, msp_pth, chunk, db_type, celery_obj=False):
        """Parse the MSP files and insert into database

        Args:
            msp_pth (str): path to msp file or directory [required]
            db_type (str): The type of database to submit to (either 'sqlite', 'mysql' or 'django_mysql') [required]
            chunk (int): Chunks of spectra to parse data (useful to control memory usage) [required]
            celery_obj (boolean): If using Django a Celery task object can be used to keep track on ongoing tasks
                              [default False]
        """

        if os.path.isdir(msp_pth):
            c = 0
            for folder, subs, files in sorted(os.walk(msp_pth)):
                for msp_file in sorted(files):
                    msp_file_pth = os.path.join(folder, msp_file)
                    if os.path.isdir(msp_file_pth) or not msp_file_pth.lower().endswith(('txt', 'msp')):
                        continue
                    print('MSP FILE PATH', msp_file_pth)

                    self.num_lines = line_count(msp_file_pth)
                    # each file is processed separately but we want to still process in chunks so we save the number
                    # of spectra currently being processed with the c variable
                    with open(msp_file_pth, "r") as f:
                        c = self._parse_lines(f, chunk, db_type, celery_obj, c)
        else:
            self.num_lines = line_count(msp_pth)
            with open(msp_pth, "r") as f:
                self._parse_lines(f, chunk, db_type, celery_obj)

        self.insert_data(remove_data=True, db_type=db_type)

    def _parse_lines(self, f, chunk, db_type, celery_obj=False, c=0):
        """Parse the MSP files and insert into database

        Args:
            f (file object): the opened file object
            db_type (str): The type of database to submit to (either 'sqlite', 'mysql' or 'django_mysql') [required]
            chunk (int): Chunks of spectra to parse data (useful to control memory usage) [required]
            celery_obj (boolean): If using Django a Celery task object can be used to keep track on ongoing tasks
                              [default False]
            c (int): Number of spectra currently processed (will reset to 0 after that chunk of spectra has been
                     inserted into the database
        """
        old = 0

        for i, line in enumerate(f):

            line = line.rstrip()

            if i == 0:
                old = self.current_id_meta

            self._update_libdata(line)

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

    def _update_libdata(self, line):
        """Update the library meta data from the current line being parsed

        Args:
            line (str): The current line of the of the file being parsed
        """
        ####################################################
        # parse MONA Comments line
        ####################################################
        # The mona msp files contain a "comments" line that contains lots of other information normally separated
        # into by ""
        if re.match('^Comment.*$', line, re.IGNORECASE):
            comments = re.findall('"([^"]*)"', line)
            for c in comments:
                self._parse_meta_info(c)
                self._parse_compound_info(c)

        ####################################################
        # parse meta and compound info lines
        ####################################################
        # check the current line for both general meta data
        # and compound information
        self._parse_meta_info(line)
        self._parse_compound_info(line)

        ####################################################
        # End of meta data
        ####################################################
        # Most MSP files have the a standard line of text before the spectra information begins. Here we check
        # for this line and store the relevant details for the compound and meta information to be ready for insertion
        # into the database
        if self.collect_meta and (re.match('^Num Peaks(.*)$', line, re.IGNORECASE) or re.match('^PK\$PEAK:(.*)', line,
                re.IGNORECASE) or re.match('^PK\$ANNOTATION(.*)', line, re.IGNORECASE)):

            self._store_compound_info()

            self._store_meta_info()

            # Reset the temp meta and compound information
            self.meta_info = get_blank_dict(self.meta_regex)
            self.compound_info = get_blank_dict(self.compound_regex)
            self.other_names = []
            self.collect_meta = False

        # ignore additional information in the 3rd column if using the MassBank spectra schema
        if re.match('^PK\$PEAK: m/z int\. rel\.int\.$', line, re.IGNORECASE):
            self.ignore_additional_spectra_info = True

        # Check if annnotation or spectra is to be in the next lines to be parsed
        if re.match('^Num Peaks(.*)$', line, re.IGNORECASE) or re.match('^PK\$PEAK:(.*)', line, re.IGNORECASE):
            self.start_spectra = True
            return
        elif re.match('^PK\$ANNOTATION(.*)', line, re.IGNORECASE):
            self.start_spectra_annotation = True

            match = re.match('^PK\$ANNOTATION:(.*)', line, re.IGNORECASE)
            columns = match.group(1)
            cl = columns.split()

            self.spectra_annotation_indexes = {i: cl.index(i) for i in cl}
            return

        ####################################################
        # Process annotation details
        ####################################################
        # e.g. molecular formula for each peak in the spectra
        if self.start_spectra_annotation:
            self._parse_spectra_annotation(line)

        ####################################################
        # Process spectra
        ####################################################
        if self.start_spectra:
            self._parse_spectra(line)

    def get_compound_ids(self):
        """Extract the current compound ids in the database. Updates the self.compound_ids list
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT inchikey_id FROM metab_compound')
        self.conn.commit()
        for row in cursor:
            if not row[0] in self.compound_ids:
                self.compound_ids.append(row[0])

    def _store_compound_info(self):
        """Update the compound_info dictionary with the current chunk of compound details

        Note that we use the inchikey as unique identifier. If we can't find an appropiate inchikey we just use
        a random string (uuid4) suffixed with UNKNOWN
        """
        other_name_l = [name for name in self.other_names if name != self.compound_info['name']]
        self.compound_info['other_names'] = ' <#> '.join(other_name_l)

        if not self.compound_info['inchikey_id']:
            self._set_inchi_pcc(self.compound_info['pubchem_id'], 'cid', 0)

        if not self.compound_info['inchikey_id']:
            self._set_inchi_pcc(self.compound_info['smiles'], 'smiles', 0)

        if not self.compound_info['inchikey_id']:
            self._set_inchi_pcc(self.compound_info['name'], 'name', 0)

        if not self.compound_info['inchikey_id']:
            print('WARNING, cant get inchi key for ', self.compound_info)
            print(self.meta_info)
            print('#########################')
            self.compound_info['inchikey_id'] = 'UNKNOWN_' + str(uuid.uuid4())

        if not self.compound_info['pubchem_id'] and self.compound_info['inchikey_id']:
            self._set_inchi_pcc(self.compound_info['inchikey_id'], 'inchikey', 0)

        if not self.compound_info['name']:
            self.compound_info['name'] = 'unknown name'

        if not self.compound_info['inchikey_id'] in self.compound_ids:
            self.compound_info_all.append(tuple(self.compound_info.values()) + (
                str(datetime.datetime.now()),
                str(datetime.datetime.now()),
            ))
            self.compound_ids.append(self.compound_info['inchikey_id'])

    def _store_meta_info(self):
        """Update the meta dictionary with the current chunk of meta data details
        """
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

    def _parse_spectra_annotation(self, line):
        """Parse and store the spectral annotation details
        """
        if re.match('^PK\$NUM_PEAK(.*)', line, re.IGNORECASE):
            self.start_spectra_annotation = False
            return

        saplist = line.split()

        sarow = (
            self.current_id_spectra_annotation,
            float(saplist[self.spectra_annotation_indexes['m/z']]) if 'm/z' in self.spectra_annotation_indexes else None,
            saplist[self.spectra_annotation_indexes[
                'tentative_formula']] if 'tentative_formula' in self.spectra_annotation_indexes else None,
            float(saplist[self.spectra_annotation_indexes[
                'mass_error(ppm)']]) if 'mass_error(ppm)' in self.spectra_annotation_indexes else None,
            self.current_id_meta)

        self.spectra_annotation_all.append(sarow)

        self.current_id_spectra_annotation += 1

    def _parse_spectra(self, line):
        """Parse and store the spectral details
        """
        if line in ['\n', '\r\n', '//\n', '//\r\n', '', '//']:
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

    def _set_inchi_pcc(self, in_str, pcp_type, elem):
        """Check pubchem compounds via API for both an inchikey and any available compound details
        """
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
        except pcp.ServerError as e:
            print(e)
            return 0
        except URLError as e:
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

    def _get_other_names(self, line):
        """Parse and extract any other names that might be recorded for the compound

        Args:
             line (str): line of the msp file
        """
        m = re.search(self.compound_regex['other_names'][0], line, re.IGNORECASE)
        if m:
            self.other_names.append(m.group(1).strip())

    def _parse_meta_info(self, line):
        """Parse and extract all meta data by looping through the dictionary of meta_info regexs

        updates self.meta_info

        Args:
             line (str): line of the msp file
        """
        if self.mslevel:
            self.meta_info['ms_level'] = self.mslevel

        for k, regexes in six.iteritems(self.meta_regex):
            for reg in regexes:

                m = re.search(reg, line, re.IGNORECASE)

                if m:
                    self.meta_info[k] = m.group(1).strip()

    def _parse_compound_info(self, line):
        """Parse and extract all compound data by looping through the dictionary of compound_info regexs

        updates self.compound_info

        Args:
             line (str): line of the msp file

        """
        for k, regexes in six.iteritems(self.compound_regex):
            for reg in regexes:
                if self.compound_info[k]:
                    continue
                m = re.search(reg, line, re.IGNORECASE)
                if m:
                    self.compound_info[k] = m.group(1).strip()

        self._get_other_names(line)

    def insert_data(self, remove_data=False, db_type='sqlite'):
        """Insert data stored in the current chunk of parsing into the selected database


        Args:
             remove_data (boolean): Remove the data stored within the LibraryData object for the current chunk of
                                    processing
             db_type (str): The type of database to submit to
                            either 'sqlite', 'mysql' or 'django_mysql' [default sqlite]
        """
        if self.update_source:
            # print "insert ref id"
            import msp2db
            self.c.execute(
                "INSERT INTO library_spectra_source (id, name, parsing_software) VALUES"
                " ({a}, '{b}', 'msp2db-v{c}')".format(a=self.current_id_origin, b=self.source, c=msp2db.__version__))
            self.conn.commit()

        if self.compound_info_all:
            self.compound_info_all = _make_sql_compatible(self.compound_info_all)

            cn = ', '.join(self.compound_info.keys()) + ',created_at,updated_at'

            insert_query_m(self.compound_info_all, columns=cn, conn=self.conn, table='metab_compound',
                           db_type=db_type)

        self.meta_info_all = _make_sql_compatible(self.meta_info_all)

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
            self._get_current_ids(source=False)

    def get_db_dict(self):
        """ Get a dictionary of the library spectra from the associated database

        Example:
            >>> from msp2db.db import create_db
            >>> from msp2db.parse import LibraryData
            >>> db_pth = 'spectral_library.db'
            >>> create_db(file_pth=db_pth, db_type='sqlite', db_name='spectra')
            >>> libdata = LibraryData(msp_pth='MoNA-export-FAHFA.msp',
            >>>                  db_pth=db_pth,
            >>>                  db_type='sqlite',
            >>>                  schema='mona',
            >>>                  source='fahfa',
            >>>                  chunk=200)
            >>> libdata.db_dict()

        If using a large database the resulting dictionary will be very large!


        Returns:
           A dictionary with the following keys 'library_spectra', 'library_spectra_meta', 'library_spectra_annotations',
           'library_spectra_source' and 'metab_compound'. Where corresponding values for each key are list of list containing
           all the rows in the database.

        """
        return db_dict(self.c)

    def close(self):
        """ Close the database connections
        """
        self.conn.close()

        # build up list of inserts

        # add in bulk the splash keys


def add_splash_ids(splash_mapping_file_pth, conn, db_type='sqlite'):
    """ Add splash ids to database (in case stored in a different file to the msp files like for MoNA)

    Example:
        >>> from msp2db.db import get_connection
        >>> from msp2db.parse import add_splash_ids
        >>> conn = get_connection('sqlite', 'library.db')
        >>> add_splash_ids('splash_mapping_file.csv', conn, db_type='sqlite')


    Args:
        splash_mapping_file_pth (str): Path to the splash mapping file (needs to be csv format and have no headers,
                                       should contain two columns. The first the accession number the second the splash.
                                       e.g. AU100601, splash10-0a4i-1900000000-d2bc1c887f6f99ed0f74 \n

    """
    # get dictionary of accession and library_spectra_meta_id
    cursor = conn.cursor()
    cursor.execute("SELECT id, accession FROM library_spectra_meta")

    accession_d = {row[1]: row[0] for row in cursor}

    if db_type == 'sqlite':
        type_sign = '?'
    else:
        type_sign = '%s'

    rows = []
    c = 0
    # loop through splash mapping file
    with open(splash_mapping_file_pth, "r") as f:

        for line in f:
            c+=1
            line = line.rstrip()
            line_l = line.split(',')

            accession = line_l[0]
            splash = line_l[1]
            try:
                aid = accession_d[accession]
            except KeyError as e:
                print("can't find accession {}".format(accession))
                continue

            row = (splash, aid)
            rows.append(row)

            if c > 200:
                print(row)
                cursor.executemany("UPDATE library_spectra_meta SET splash = {t} WHERE id = {t} ".format(t=type_sign), rows)
                conn.commit()
                rows = []
                c = 0

    cursor.executemany("UPDATE library_spectra_meta SET splash = {t} WHERE id = {t} ".format(t=type_sign), rows)
    conn.commit()


