# Veterinary Patholgy Database Scripts

### These scripts are meant for the use of the Maley lab, Biodesign Institute, Arizona State University
### Copyright 2018 by Shawn Rupp

## Installation 
### Database Scripts
	git clone https://github.com/icwells/veterinaryPathology.git 
### Kestrel 
	git clone https://github.com/icwells/Kestrel.git 
### excelToText
	git clone https://github.com/icwells/unicodeTools.git 

## Usage 

### Converting the MSU databse to csv
The MSU database had to be converted into a single csv in two steps. First, the directory of xlsx files were 
converted into csv files using excelToText.py, located here: https://github.com/icwells/unicodeTools 

Next the directory of csv records were merged into a single csv with the description lines appended to the 
end of the individual records, resulting in one line per record.

	python msuDB.py -i path/to/directory -o path/to/output/file

### mergeTaxonomy.py
The original taxonomy merging scripts were placed into one script to keep things organized (they can still be 
found in the databaseSpecific folder for the time being).

	python mergeTaxonomy.py -n/m/z path/to/DB -t path/to/kestrel/output -o output/file 

	-h, --help	show this help message and exit 
	--cancer	Only extracts and concatenates cancer records (NWZP only; extracts all records by default). 
	-n N		Path to NWZP file (utf-8 encoded). 
	-m M		Path to MSU file (utf-8 encoded). 
	-z Z		Path to ZEPS file (utf-8 encoded). 
	-t T		Path to taxonomy file. 
	-r R		Path to records file with age, sex, and cancer type (NWZP only; not required). 
	-o O		Output file.  

### extractAgeSexDiagnosis.py
This script will extract age, sex, and cancer type and location from the input file. Make sure cancerdict.tsv is in the same directory. 

	python extractNWZP.py -c column -i path/to/records/file -o path/to/output

	-h, --help	show this help message and exit
	-i I		Path to input file.
	-o O		Output file.
	-c C		ID column number (first column by default).

### getEntries.py
This script can be used to count the number of unique entries found in a given column of a file, extract values from a given column, or identify multiple entries.

	-h, --help	show this help message and exit
	-c C		Column number to analyze.
	-v V		Value from column c to extract (leave blank to count).
	--multiple	Writes entries with multiple occurances from column c to output file (will append to existing output file).
	--empty		Writes entries with no entry in column c to output file (will append to existing output file).
	-i I		Path to input file.
	-o O		Path to output file (not required for counting). 

### cancerOccurances.py
This script will count the number of cancer occurances per species and per database.  

	python cancerOccurances.py -n path/to/nwzp -m path/to/msu -z path/to/zeps -o output/file

	-h, --help	show this help message and exit
	-n N		Path to NWZP file.
	-m M		Path to merged MSU file.
	-z Z		Path to ZEPS species count file (with scientific names).
	-o O		Path to output file.
