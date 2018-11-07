# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from msp2db.parse import LibraryData
from msp2db.db import create_db

db_pth = '/home/tomnl/spectral_library_07112018v1.db'

#############################################################
# Create database
#############################################################
create_db(file_pth=db_pth, db_type='sqlite', db_name='spectra')



#############################################################
# FAHFA
#############################################################
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-FAHFA.msp',

                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='fahfa',
                      mslevel=None,
                      chunk=200)

#############################################################
# GNPS
#############################################################
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-GNPS.msp',

                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='gnps',
                      mslevel=None,
                      chunk=200)

#############################################################
# HMDB
#############################################################
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-HMDB.msp',

                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='hmdb',
                      mslevel=None,
                      chunk=200)


#############################################################
# RTX5_Fiehnlib
#############################################################
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-RTX5_Fiehnlib.msp',
                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='rtx5_fiehnlib',
                      mslevel=None,
                      chunk=200)



#############################################################
# MoNA-export-Vaniya-Fiehn_Natural_Products_Library
#############################################################
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-Vaniya-Fiehn_Natural_Products_Library.msp',
                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='vaniya_fiehn_natural_products_library',
                      mslevel=None,
                      chunk=200)


#############################################################
# Fiehn_HILIC
#############################################################
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-Fiehn_HILIC.msp',
                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='fiehn_hilic',
                      mslevel=None,
                      chunk=200)


#############################################################
# MoNA-export-ReSpect
#############################################################
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-ReSpect.msp',
                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='respect',
                      mslevel=None,
                      chunk=200)

#############################################################
# Massbank
#############################################################
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-MassBank.msp',
                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='massbank',
                      mslevel=None,
                      chunk=200)


#############################################################
# lipidblast
#############################################################
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-LipidBlast.msp',
                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='lipidblast',
                      mslevel=None,
                      chunk=200)


#############################################################
# MetaboBASE
#############################################################
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-MetaboBASE.msp',
                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='metabobase',
                      mslevel=None,
                      chunk=200)


#############################################################
# MoNA-export-Pathogen_Box
#############################################################
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-Pathogen_Box.msp',
                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='pathogen_box',
                      mslevel=None,
                      chunk=200)


#############################################################
# RIKEN_IMS_Oxidized_Phospholipids
#############################################################
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-RIKEN_IMS_Oxidized_Phospholipids.msp',
                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='riken_ims_oxidized_phospholipids',
                      mslevel=None,
                      chunk=200)

