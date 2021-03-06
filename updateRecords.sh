#!/bin/bash

##############################################################################
#	Updates full records files with taxonomies and diagnoses
##############################################################################

# MSU
python mergeTaxonomy.py -t /home/shawn/Documents/Git/comparativeoncologydata/taxonomy.190312.csv -r /home/shawn/Documents/Git/comparativeoncologydata/MSU/msu_diagnoses.csv -i /home/shawn/Documents/Git/comparativeoncologydata/MSU/msu_masterfile.csv -o /home/shawn/Documents/Git/comparativeoncologydata/MSU/msu_Full_Taxonomy.csv

# NWZP
python mergeTaxonomy.py -t /home/shawn/Documents/Git/comparativeoncologydata/taxonomy.190312.csv -r /home/shawn/Documents/Git/comparativeoncologydata/NWZP/diagnoses/nwzpDiagnoses.csv -i /home/shawn/Documents/Git/comparativeoncologydata/NWZP/fulldata.UTF.csv -o /home/shawn/Documents/Git/comparativeoncologydata/NWZP/NWZP_fullRecords.csv

# ZEPS
python mergeTaxonomy.py -t /home/shawn/Documents/Git/comparativeoncologydata/taxonomy.190312.csv -r /home/shawn/Documents/Git/comparativeoncologydata/ZEPS/ZEPS_diagnoses.csv -i /home/shawn/Documents/Git/comparativeoncologydata/ZEPS/ZEPS_data_clean.csv -o /home/shawn/Documents/Git/comparativeoncologydata/ZEPS/ZEPS_fullRecords.csv

# Also update necropsies and species totals
python getEntries.py -c Necropsy -v Y -i /home/shawn/Documents/Git/comparativeoncologydata/NWZP/NWZP_fullRecords.csv -o /home/shawn/Documents/Git/comparativeoncologydata/NWZP/nwzpNecropsies.csv

python cancerOccurances.py -d /home/shawn/Documents/Git/comparativeoncologydata/Duke/dlcTaxonomy.csv -m /home/shawn/Documents/Git/comparativeoncologydata/MSU/msu_Full_Taxonomy.csv -n /home/shawn/Documents/Git/comparativeoncologydata/NWZP/NWZP_fullRecords.csv -z /home/shawn/Documents/Git/comparativeoncologydata/ZEPS/Species_list_Drury_2017-10-23.withTaxonomies.csv -o /home/shawn/Documents/Git/comparativeoncologydata/species.csv

