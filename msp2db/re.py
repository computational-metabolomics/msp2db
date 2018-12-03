#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals, print_function
import collections

def get_meta_regex(schema='mona'):
    """ Create a dictionary of regex for extracting the meta data for the spectra
    """
    # NOTE: will just ignore cases, to avoid repetition here
    meta_parse = collections.OrderedDict()

    if schema == 'mona':
        meta_parse['collision_energy'] = ['^collision energy(?:=|:)(.*)$']
        meta_parse['ms_level'] = ['^ms.*level(?:=|:)\D*(\d*)$', '^ms type(?:=|:)\D*(\d*)$',
                              '^Spectrum_type(?:=|:)\D*(\d*)$']
        meta_parse['accession'] = ['^accession(?:=|:)(.*)$', '^DB#(?:=|:)(.*)$']
        meta_parse['resolution'] = ['^resolution(?:=|:)(.*)$']
        meta_parse['polarity'] = ['^ion.*mode(?:=|:)(.*)$', '^ionization.*mode(?:=|:)(.*)$', '^polarity(?:=|:)(.*)$']
        meta_parse['fragmentation_type'] = ['^fragmentation.*mode(?:=|:)(.*)$', '^fragmentation.*type(?:=|:)(.*)$']
        meta_parse['precursor_mz'] = ['^precursor m/z(?:=|:)\s*(\d*[.,]?\d*)$', '^precursor.*mz(?:=|:)\s*(\d*[.,]?\d*)$']
        meta_parse['precursor_type'] = ['^precursor.*type(?:=|:)(.*)$', '^adduct(?:=|:)(.*)$']
        meta_parse['instrument_type'] = ['^instrument.*type(?:=|:)(.*)$']
        meta_parse['instrument'] = ['^instrument(?:=|:)(.*)$']
        meta_parse['copyright'] = ['^copyright(?:=|:)(.*)$']
        # meta_parse['column'] = ['^column(?:=|:)(.*)$']
        meta_parse['mass_accuracy'] = ['^mass.*accuracy(?:=|:)\s*(\d*[.,]?\d*)$']
        meta_parse['mass_error'] = ['^mass.*error(?:=|:)\s*(\d*[.,]?\d*)$']
        meta_parse['origin'] = ['^origin(?:=|:)(.*)$']
        meta_parse['name'] = ['^Name(?:=|:)(.*)$']
        meta_parse['splash'] = ['^splash:(.*)$']
        meta_parse['retention_time'] = ['^retention.*time(?:=|:)\s*(\d*[.,]?\d*)$']
        meta_parse['retention_index'] = ['^retention.*index(?:=|:)\s*(\d*[.,]?\d*)$']

    elif schema == 'massbank':
        meta_parse['collision_energy'] = ['^AC\$MASS_SPECTROMETRY:\s+COLLISION_ENERGY\s+(.*)$']
        meta_parse['ms_level'] = ['^AC\$MASS_SPECTROMETRY:\s+MS_TYPE\s+\D*(\d*)$']
        meta_parse['accession'] = ['^ACCESSION:(.*)$']
        meta_parse['resolution'] = ['^AC\$MASS_SPECTROMETRY:\s+RESOLUTION\s+(.*)$']
        meta_parse['polarity'] = ['^AC\$MASS_SPECTROMETRY:\s+ION_MODE\s+(.*)$']
        meta_parse['fragmentation_type'] = ['^AC\$MASS_SPECTROMETRY:\s+FRAGMENTATION_MODE\s+(.*)$']
        meta_parse['precursor_mz'] = ['^MS\$FOCUSED_ION:\s+PRECURSOR_M/Z\s+(\d*[.,]?\d*)$']
        meta_parse['precursor_type'] = ['^MS\$FOCUSED_ION:\s+PRECURSOR_TYPE\s+(.*)$']
        meta_parse['instrument_type'] = ['^AC\$INSTRUMENT_TYPE:\s+(.*)$']
        meta_parse['instrument'] = ['^AC\$INSTRUMENT:\s+(.*)$']
        meta_parse['copyright'] = ['^COPYRIGHT:\s+(.*)']
        # meta_parse['column'] = ['^column(?:=|:)(.*)$']
        meta_parse['mass_accuracy'] = ['^AC\$MASS_SPECTROMETRY:\s+ACCURACY\s+(.*)$']  # need to check
        meta_parse['mass_error'] = ['^AC\$MASS_SPECTROMETRY:\s+ERROR\s+(.*)$']  # need to check
        meta_parse['splash'] = ['^PK\$SPLASH:\s+(.*)$']
        meta_parse['origin'] = ['^origin(?:=|:)(.*)$']
        meta_parse['name'] = ['^RECORD_TITLE:\s+(.*)$']
        meta_parse['retention_time'] = ['^AC\$CHROMATOGRAPHY:\s+RETENTION.*TIME\s+(\d*[.,]?\d*)$']
        meta_parse['retention_index'] = ['^AC\$CHROMATOGRAPHY:\s+RETENTION.*INDEX\s+(\d*[.,]?\d*)$']




    return meta_parse


def get_compound_regex(schema='mona'):
    """ Create a dictionary of regex for extracting the compound information for the spectra
    """

    # NOTE: will just ignore cases in the regex, to avoid repetition here
    meta_parse = collections.OrderedDict()

    if schema == 'mona':
        meta_parse['name'] = ['^Name(?:=|:)(.*)$']
        meta_parse['inchikey_id'] = ['^inchikey(?:=|:)(.*)$']
        meta_parse['molecular_formula'] = ['^molecular formula(?:=|:)(.*)$', '^formula:(.*)$']
        meta_parse['molecular_weight'] = ['^MW(?:=|:)(\d*[.,]?\d*)$']
        meta_parse['pubchem_id'] = ['^pubchem.*cid(?:=|:)(\d*)".*$']
        meta_parse['chemspider_id'] = ['^chemspider(?:=|:)(\d*)".*$']
        meta_parse['compound_class'] = ['^compound.*class(?:=|:)(.*)$']
        meta_parse['exact_mass'] = ['^exact.*mass(?:=|:)(\d*[.,]?\d*)$']
        meta_parse['smiles'] = ['^SMILES(?:=|:)(.*)$']
        meta_parse['other_names'] = ['^Synonym(?:=|:)(.*)$']
    elif schema == 'massbank':
        meta_parse['name'] = ['^CH\$NAME:\s+(.*)$']
        meta_parse['other_names'] = ['^CH\$NAME:\s+(.*)$']

        meta_parse['inchikey_id'] = ['^CH\$LINK:\s+INCHIKEY\s+(.*)$']
        meta_parse['molecular_formula'] = ['^CH\$FORMULA:\s+(.*)$']
        meta_parse['molecular_weight'] = ['^CH\$MOLECULAR_WEIGHT:\s+(.*)$']
        meta_parse['pubchem_id'] = ['^CH\$LINK:\s+PUBCHEM\s+CID:(.*)$']
        meta_parse['chemspider_id'] = ['^CH\$LINK:\s+CHEMSPIDER\s+(.*)$']
        meta_parse['compound_class'] = ['^CH\$COMPOUND_CLASS:\s+(.*)$']
        meta_parse['exact_mass'] = ['^CH\$EXACT_MASS:\s+(.*)$']
        meta_parse['smiles'] = ['^CH\$SMILES:\s+(.*)$']

    return meta_parse
