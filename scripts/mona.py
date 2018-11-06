# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from msp2db.msp2db import LibraryData, create_db

db_pth = 'spectral_library_06112018v4.db'

#############################################################
# Create database
#############################################################
create_db(file_pth=db_pth, db_type='sqlite', db_name='spectra')


# #############################################################
# # Massbank
# #############################################################
# libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-MassBank.msp',
#                       name='massbank',
#                       db_pth=db_pth,
#                       db_type='sqlite',
#                       d_form=None,
#                       schema='mona',
#                       source='massbank',
#                       mslevel=None,
#                       chunk=200)
#
#
# #############################################################
# # lipidblast
# #############################################################
# libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-LipidBlast.msp',
#                       name='massbank',
#                       db_pth=db_pth,
#                       db_type='sqlite',
#                       d_form=None,
#                       schema='mona',
#                       source='lipidblast',
#                       mslevel=None,
#                       chunk=200)
#
#
# #############################################################
# # MetaboBASE
# #############################################################
# libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-MetaboBASE.msp',
#                       name='MetaboBASE',
#                       db_pth=db_pth,
#                       db_type='sqlite',
#                       d_form=None,
#                       schema='mona',
#                       source='MetaboBASE',
#                       mslevel=None,
#                       chunk=200)




# #############################################################
# # MoNA-export-Pathogen_Box
# #############################################################
# libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-Pathogen_Box.msp',
#                       name='pathogen',
#                       db_pth=db_pth,
#                       db_type='sqlite',
#                       d_form=None,
#                       schema='mona',
#                       source='pathogen',
#                       mslevel=None,
#                       chunk=200)
#
#
# #############################################################
# # MoNA-export-Pathogen_Box
# #############################################################
# libdata = LibraryData(msp_pth='/media/sf_DATA/mona/MoNA-export-RIKEN_IMS_Oxidized_Phospholipids.msp',
#                       name='Phospholipids',
#                       db_pth=db_pth,
#                       db_type='sqlite',
#                       d_form=None,
#                       schema='mona',
#                       source='Phospholipids',
#                       mslevel=None,
#                       chunk=200)
#




#############################################################
# TESTING
#############################################################
libdata = LibraryData(msp_pth='/media/sf_DATA/mona/test/MoNA-export-Pathogen_Box-small.msp',

                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='pathogen',
                      mslevel=None,
                      chunk=200)

libdata = LibraryData(msp_pth='/media/sf_DATA/mona/test/MoNA-export-MassBank-small.msp',

                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='massbank',
                      mslevel=None,
                      chunk=200)

libdata = LibraryData(msp_pth='/media/sf_DATA/mona/test/MoNA-export-MetaboBASE-small.msp',

                      db_pth=db_pth,
                      db_type='sqlite',
                      d_form=None,
                      schema='mona',
                      source='metabobase',
                      mslevel=None,
                      chunk=200)

