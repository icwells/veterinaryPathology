# Veterinary Patholgy Database Scripts

### These scripts are meant for the use of the Maley lab, Biodesign Institute, Arizona State University
### Copyright 2018 by Shawn Rupp

## Dependencies
Python3 
excelToText.py 
Kestrel 

## Installation 
### Database Scripts
	git clone https://github.com/icwells/veterinaryPathology.git 
### Kestrel 
	git clone https://github.com/icwells/Kestrel.git 
### excelToText
	git clone https://github.com/icwells/excelToText.git 

## Usage 

### Converting the MSU databse to csv
The MSU database had to be converted into a single csv in two steps. First, the directory of xlsx files were 
converted into csv files using excelToText.py, located here: https://github.com/icwells/excelToText 

Next the directory of csv records were merged into a single csv with the description lines appended to the 
end of the individual records, resulting in one line per record.

	python msuDB.py -i path_to_directory -o path_to_output_file

### Taxonomy Merging Scripts
Each taxonomy merging script functions the same way (replace the "..." with the name of the specific script):

	python ...Taxonomy.py -i path_to_zepsDB -t path_to_kestrel_output -o output_file 

