# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals
import time
import datetime
import sys
import csv
import os
import shutil
from msp2db.parse import LibraryData
from msp2db.db import create_db

ts = time.time()

st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S')

db_pth = sys.argv[1]

file_size_check_pth = os.path.join(sys.argv[2], 'file_size_check.csv')
print(file_size_check_pth)
#############################################################
# Create database
#############################################################
create_db(file_pth=db_pth)
with open(file_size_check_pth, 'w') as fsc:
    dw = csv.DictWriter(fsc, fieldnames=['source', 'size', 'diff'])
    dw.writeheader()
    print("#############################################################")
    print('# FAHFA')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-FAHFA.msp', 
                          db_pth=db_pth,
                          db_type='sqlite',
                          schema='mona',
                          source='fahfa',
                          mslevel=None,
                          chunk=200)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + '_FAHFA.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)

    dw.writerow( {'source':'fahfa', 'size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth) })
    old_size = os.path.getsize(db_pth)
    print("#############################################################")
    print('# GNPS')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-GNPS.msp',
                          db_pth=db_pth,
                          db_type='sqlite',
                          schema='mona',
                          source='gnps',
                          mslevel=None,
                          chunk=200)
    dw.writerow({'source': 'gnps', 'size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth) })
    old_size = os.path.getsize(db_pth)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'GNPS.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)

    print("#############################################################")
    print('# HMDB')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-HMDB.msp',
                          db_pth=db_pth,
                          db_type='sqlite',
                          schema='mona',
                          source='hmdb',
                          mslevel=None,
                          chunk=200)
    dw.writerow({'source': 'hmdb','size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth)-old_size })
    old_size = os.path.getsize(db_pth)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'HMDB.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)

    print("#############################################################")
    print('# RTX5_Fiehnlib')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-RTX5_Fiehnlib.msp',
                          db_pth=db_pth,
                          db_type='sqlite',

                          schema='mona',
                          source='rtx5_fiehnlib',
                          mslevel=None,
                          chunk=200)
    dw.writerow({'source': 'fiehn_rtx5', 'size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth)-old_size })
    old_size = os.path.getsize(db_pth)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'RTX5.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)


    print("#############################################################")
    print('# MoNA-export-Vaniya-Fiehn_Natural_Products_Library')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-Vaniya-Fiehn_Natural_Products_Library.msp',
                          db_pth=db_pth,
                          db_type='sqlite',
                          schema='mona',
                          source='vaniya_fiehn_natural_products_library',
                          mslevel=None,
                          chunk=200)
    
    dw.writerow({'source': 'vaniya', 'size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth)-old_size })
    old_size = os.path.getsize(db_pth)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'VANIYA.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)


    print("#############################################################")
    print('# Fiehn_HILIC')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-Fiehn_HILIC.msp',
                          db_pth=db_pth,
                          db_type='sqlite',
                          schema='mona',
                          source='fiehn_hilic',
                          mslevel=None,
                          chunk=200)
    dw.writerow({'source': 'fiehn_hilic', 'size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth)-old_size })
    old_size = os.path.getsize(db_pth)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'FIEHN_HILIC.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)


    print("#############################################################")
    print('# MoNA-export-ReSpect')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-ReSpect.msp',
                          db_pth=db_pth,
                          db_type='sqlite',

                          schema='mona',
                          source='respect',
                          mslevel=None,
                          chunk=200)
    dw.writerow({'source': 'respect', 'size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth)-old_size })
    old_size = os.path.getsize(db_pth)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'RESPECT.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)


    print("#############################################################")
    print('# Massbank')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-MassBank.msp',
                          db_pth=db_pth,
                          db_type='sqlite',
                          schema='mona',
                          source='massbank',
                          mslevel=None,
                          chunk=200)
    dw.writerow({'source': 'massbank', 'size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth)-old_size })
    old_size = os.path.getsize(db_pth)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'MASSBANK.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)



    print("#############################################################")
    print('# lipidblast')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-LipidBlast.msp',
                          db_pth=db_pth,
                          db_type='sqlite',
                          schema='mona',
                          source='lipidblast',
                          mslevel=None,
                          chunk=200)
    dw.writerow({'source': 'lipidblast', 'size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth)-old_size })
    old_size = os.path.getsize(db_pth)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'LIPIDBLAST.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)

    print("#############################################################")
    print('# MetaboBASE')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-MetaboBASE.msp',
                          db_pth=db_pth,
                          db_type='sqlite',
                          schema='mona',
                          source='metabobase',
                          mslevel=None,
                          chunk=200)
    dw.writerow({'source': 'metabobase', 'size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth)-old_size })
    old_size = os.path.getsize(db_pth)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'METABOBASE.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)



    print("#############################################################")
    print('# MoNA-export-Pathogen_Box')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-Pathogen_Box.msp',
                          db_pth=db_pth,
                          db_type='sqlite',
                          schema='mona',
                          source='pathogen_box',
                          mslevel=None,
                          chunk=200)
    dw.writerow({'source': 'pathogenbox', 'size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth)-old_size })
    old_size = os.path.getsize(db_pth)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'PATHOGENBOX.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)



    print("#############################################################")
    print('# RIKEN_IMS_Oxidized_Phospholipids')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-RIKEN_IMS_Oxidized_Phospholipids.msp',
                          db_pth=db_pth,
                          db_type='sqlite',
                          schema='mona',
                          source='riken_ims_oxidized_phospholipids',
                          mslevel=None,
                          chunk=200)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'RIKEN_OX.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)

    print("#############################################################")
    print('# Fiehn Plasma')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-RIKEN_PlaSMA.msp',
                          db_pth=db_pth,
                          db_type='sqlite',
                          schema='mona',
                          source='fiehn_plasma',
                          mslevel=None,
                          chunk=200)

    dw.writerow({'source':'fiehn_plasma','size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth)-old_size })
    old_size = os.path.getsize(db_pth)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'FIEHN_PLASMA.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)


    print("#############################################################")
    print('# EBML-MCF')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-EMBL-MCF.msp',
                          db_pth=db_pth,
                          db_type='sqlite',
                          schema='mona',
                          source='embl_mcf',
                          mslevel=None,
                          chunk=200)

    dw.writerow({'source':'embl-mcf','size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth)-old_size })
    old_size = os.path.getsize(db_pth)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'EBML.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)


    print("#############################################################")
    print('# Volatile_FiehnLib')
    print("#############################################################")
    libdata = LibraryData(msp_pth='MoNA-export-Volatile_FiehnLib.msp',
                          db_pth=db_pth,
                          db_type='sqlite',
                          schema='mona',
                          source='volatile_fienlib',
                          mslevel=None,
                          chunk=200)

    dw.writerow({'source':'volatile_fiehnLib','size':os.path.getsize(db_pth), 'diff':os.path.getsize(db_pth)-old_size })
    old_size = os.path.getsize(db_pth)
    db_pth_copy = os.path.join(sys.argv[2], datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S') + 'VOLATILE_FIEHN.sqlite')
    shutil.copyfile(db_pth, db_pth_copy)







