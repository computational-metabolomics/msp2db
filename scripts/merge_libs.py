import sqlite3
import sys
from msp2db.db import get_connection, db_dict, insert_query_m

#  Short script to combine databases will merge any duplicate
#  compound data based on the inchikey but assumes no duplicate spectra between both databases
db_pth_1 = sys.argv[1]
db_pth_2 = sys.argv[2]


conn1 = get_connection('sqlite', db_pth_1)
c1 = conn1.cursor()

# Get the last id for each of the tables

c1.execute('SELECT MAX(id) FROM library_spectra_source')
library_spectra_source_count_id = [i for i in c1][0][0]

c1.execute('SELECT MAX(id) FROM library_spectra_meta')
library_spectra_meta_count_id = [i for i in c1][0][0]

c1.execute('SELECT MAX(id) FROM library_spectra')
library_spectra_count_id = [i for i in c1][0][0]

conn2 = get_connection('sqlite', db_pth_2)

db_d2 = db_dict(conn2.cursor())


# Import source data
new_library_spectra_source = [(i+library_spectra_source_count_id, *x[1:len(x)]) for i, x in enumerate(db_d2['library_spectra_source'], 1)]
insert_query_m(new_library_spectra_source, 'library_spectra_source', conn1, db_type='sqlite')

# Import Meta data
new_library_spectra_meta = [(i+library_spectra_meta_count_id, *x[1:len(x)]) for i, x in enumerate(db_d2['library_spectra_meta'], 1)]
insert_query_m(new_library_spectra_meta, 'library_spectra_meta', conn1, db_type='sqlite')

# Import spectra
new_library_spectra = [(i+library_spectra_count_id, *x[1:len(x)]) for i, x in enumerate(db_d2['library_spectra'], 1)]
insert_query_m(new_library_spectra, 'library_spectra', conn1, db_type='sqlite')


# Import metab compound data
new_inchikeys = list(set([i[len(i)-1] for i in new_library_spectra_meta]))

c1.execute('SELECT inchikey_id FROM metab_compound')
old_inchikeys = [i[0] for i in c1]

new_metab_compounds = []

new_metab_compound_d = {i[0]: i for i in db_d2['metab_compound']}

for inchikey in new_inchikeys:
    if inchikey not in old_inchikeys:
        new_metab_compounds.append(new_metab_compound_d[inchikey])

insert_query_m(new_metab_compounds, 'metab_compound', conn1, db_type='sqlite')
