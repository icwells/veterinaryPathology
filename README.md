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

	python msuDB.py -i path_to_directory -o path_to_output_file

### Taxonomy Merging Scripts
Each taxonomy merging script functions the same way (replace the "..." with the name of the specific script):

	python ...Taxonomy.py -i path_to_zepsDB -t path_to_kestrel_output -o output_file 

The zooPathTaxonomy.py script has two additional parameters: 
"-r" incorporates the age, sex, and cancer type from the output of extractNWZP.py into the merged output file. 
"--cancer" will tell the script to print only cancer records to file. 

### extractNWZP.py
This script will extract age, sex, and cancer type and location from the downloaded NWZP records.

	python extractNWZP.py -i path_to_records_file -o path_to_output

### getEntries.py
This script can be used to count the number of unique entries found in a given column of a file, extract values from a given column, or identify multiple entries.

	-h, --help	show this help message and exit
	-c C		Column number to analyze.
	-v V		Value from column c to extract (leave blank to count).
	--multiple	Writes entries with multiple occurances from column c to output
					file (will append to existing output file).
	--empty		Writes entries with no entry in column c to output file (will
					append to existing output file).
	-i I		Path to input file.
	-o O		Path to output file (not required for counting). 

