# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals
import time
import datetime
import sys
import csv
import os
from msp2db.parse import LibraryData
from msp2db.db import create_db

ts = time.time()

st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S')

db_pth = os.path.join(sys.argv[1], 'spectral_library_massbank_gnps_lipidblast_hmdb_{}.db'.format(st))



#############################################################
# Create database
#############################################################
create_db(file_pth=db_pth)



print("#############################################################")
print('# GNPS')
print("#############################################################")
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-GNPS.msp',

                      db_pth=db_pth,
                      db_type='sqlite',

                      schema='mona',
                      source='gnps',
                      mslevel=None,
                      chunk=200)

print("#############################################################")
print('# HMDB')
print("#############################################################")
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-HMDB.msp',

                      db_pth=db_pth,
                      db_type='sqlite',

                      schema='mona',
                      source='hmdb',
                      mslevel=None,
                      chunk=200)




print("#############################################################")
print('# Massbank')
print("#############################################################")
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-MassBank.msp',
                      db_pth=db_pth,
                      db_type='sqlite',
                      schema='mona',
                      source='massbank',
                      mslevel=None,
                      chunk=200)

print("#############################################################")
print('# lipidblast')
print("#############################################################")
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-LipidBlast.msp',
                      db_pth=db_pth,
                      db_type='sqlite',
                      schema='mona',
                      source='lipidblast',
                      mslevel=None,
                      chunk=200)

