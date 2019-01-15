'''This script will concatenate a given database with Kestrel taxonomy results and diagnosis records'''

import os
from datetime import datetime
from argparse import ArgumentParser
from vetPathUtils import *

BLANKRECORD = ["NA","NA","NA","NA","NA","NA","NA","NA","NA"]

def printTotal(count, total):
	# Prints number of taxonomies found
	print(("\tFound taxonomies for {:,} of {:,} entries.").format(count, total))

def formatRow(c, taxa, line, r):
	# Formats line from fulldata file
	row = []
	if c == True:
		if "8" not in line[8]:
			# Skip non-cancer records
			return None 
	n = line[6]
	if n in taxa.keys():
		# Common and scientific names
		row = [line[0], n, taxa[n][-1]]
		for i in taxa[n][:-1]:
			# Append remainder of taxonomy
			row.append(i)
		row.extend(r)
		# Add remaining data from database
		row.extend([line[8].replace(",",";"), line[9].replace(",", ";"), line[3], 
					line[7].replace(",",";"), line[5], line[1], line[2]])
	return row

def sortNWZP(c, taxa, rec, infile, outfile):
	# Sorts database and writes out relevant data with taxonomy
	first = True
	count = 0
	total = 0
	print("\n\tMerging NWZP taxonomy data...")
	with open(outfile, "w") as output:
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					total += 1
					r = BLANKRECORD
					line = line.strip().split(",")
					if len(line) >= 7:
						if rec:
							if line[0] in rec.keys():
								# Get diagnosis records
								r = rec[line[0]]
						row = formatRow(c, taxa, line, r)
						if row:
							output.write(",".join(row) + "\n")
							count += 1
				else:
					output.write("ID,CommonName,ScientificName,Kingdom,Phylum,Class,Order,Family,Genus,\
Age(months),Sex,Castrated,Location,Type,Malignant,PrimaryTumor,Metastasis,Necropsy,\
Code,Diagnosis,Case,Patient#,DateRcvd,Client,Account\n")
					first = False
	printTotal(count, total)

def sortZEPS(taxa, rec, infile, outfile):
	# Sorts database and writes out relevant data with taxonomy
	first = True
	count = 0
	total = 0
	print("\n\tMerging ZEPS taxonomy data...")
	with open(outfile, "w") as output:
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					total += 1
					r = BLANKRECORD
					line = line.strip().split(delim)
					if len(line) == 6:
						if rec:
							if line[0] in rec.keys():
								# Get diagnosis records
								r = rec[line[0]]
						n = line[2]
						if n in taxa.keys():
							row = line[:3]
							row.append([taxa[n][-1]][0])
							row.extend(taxa[n][:-1])
							row.extend(r)
							row.append(line[-1])
							if row:
								output.write(",".join(row) + "\n")
								count += 1
				else:
					output.write("Access#,Category,Breed,ScientificName,Kingdom,\
Phylum,Class,Order,Family,Genus,Age(months),Sex,Castrated,Location,Type,\
Malignant,PrimaryTumor,Metastasis,Necropsy,Diagnosis\n")
					if "\t" in line:
						delim = "\t"
					else:
						delim = ","
					first = False
	printTotal(count, total)

def sortMSU(taxa, rec, infile, outfile):
	# Sorts database and writes out relevant data with taxonomy
	first = True
	count = 0
	total = 0
	print("\n\tMerging MSU taxonomy data...")
	with open(outfile, "w") as output:
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					total += 1
					r = BLANKRECORD
					line = line.strip().split(delim)
					if len(line) >= 6:
						if rec:
							if line[0] in rec.keys():
								# Get diagnosis records
								r = rec[line[0]]
						n = line[5]
						if n in taxa.keys():
							row = line[:6]
							row.append([taxa[n][-1]][0])
							row.extend(taxa[n][:-1])
							row.extend(r)
							row.append(line[-1])
							if row:
								output.write(",".join(row) + "\n")
								count += 1
				else:
					output.write("ID,Date,Owner,Name,Species,Breed,ScientificName,\
Kingdom,Phylum,Class,Order,Family,Genus,Age(months),Sex,Castrated,Location,Type,\
Malignant,PrimaryTumor,Metastasis,Necropsy,Diagnosis\n")
					delim = getDelim(line)
					first = False
	printTotal(count, total)

def sortDLC(cancer, taxa, infile, outfile):
	# Merges duke data with taxonomy
	first = True
	count = 0
	total = 0
	print("\n\tMerging Duke taxonomy data...")
	with open(outfile, "w") as output:
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					total += 1
					line = line.strip().split(d)
					if len(line) >= c.Max:
						if cancer == False or line[c.Code] == "Yes":
							n = line[c.Species]
							if n in taxa.keys():
								row = [line[c.Submitter], line[c.ID], n]
								row.extend(taxa[n][:-1])
								row.extend([line[c.Age], line[c.Sex]])
								row.extend(line[c.Age+1:])
								if row:
									output.write(",".join(row) + "\n")
									count += 1
				else:
					output.write("Institution,ID,ScientificName,Kingdom,Phylum,Class,Order,Family,Genus,\
Age(months),Sex,CancerY/N,CancerType,Tissue,Metastatic,Widespread,DeathViaCancer,Old/NewWorld,CommonName\n")
					d = getDelim(line)
					c = Columns(line.split(d))
					first = False
	printTotal(count, total)

#-----------------------------------------------------------------------------

def getRecords(infile):
	# Reads in dictionary of age, sex, and cancer type
	first = True
	rec = {}
	print("\tReading diagnosis records...")
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				line = line.strip().split(",")
				# {ID: [age, sex, type]}
				rec[line[0]] = line[1:]
			else:
				first = False
	print(("\tFound {:,} diagnosis records.").format(len(rec.keys())))
	return rec

def getTaxa(infile):
	# Reads in taxonomy dictionary
	first = True
	taxa = {}
	species = set()
	print("\n\tReading taxonomies...")
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				line = line.split(",")
				# Query name: [taxonomy] (drops search term and urls)
				if len(line) >= 9:
					taxa[line[0]] = line[2:9]
					species.add(line[8])
			else:
				first = False
	print(("\tFound {:,} taxonomies with {:,} unique species.").format(len(taxa.keys()), len(species)))
	return taxa

def checkArgs(args):
	# Checks args for errors
	if not args.o:
		printError("Please specify an output file")
	if not args.t:
		printError("Please specify a taxonomy file")
	if not os.path.isfile(args.t):
		printError(("Cannot find {}").format(args.t))
	if not args.i:
		printError("Please specify an input file")
	return args

def main():
	start = datetime.now()
	parser = ArgumentParser("This script will concatenate a given \
database with Kestrel taxonomy results and diagnosis records.")
	parser.add_argument("--cancer", action = "store_true", default = False,
help = "Only extracts and concatenates cancer records (NWZP/DLC only; extracts all records by default).")
	parser.add_argument("-i", help = "Path to utf-8 encoded input file.")
	parser.add_argument("-t", help = "Path to taxonomy file.")
	parser.add_argument("-r", default = None,
help = "Path to records file with age, sex, and cancer type (not required).")
	parser.add_argument("-o", help = "Output file.")
	args = checkArgs(parser.parse_args())
	s = getService(args.i)
	taxa = getTaxa(args.t)
	# Check for diagnosis records
	rec = None
	if args.r:
		rec = getRecords(args.r)
	if s == "DLC":
		sortDLC(args.cancer, taxa, args.i, args.o)
	elif s == "MSU":
		sortMSU(taxa, rec, args.i, args.o)
	elif s == "NWZP":
		sortNWZP(args.cancer, taxa, rec, args.i, args.o)
	elif s == "ZEPS":
		sortZEPS(taxa, rec, args.i, args.o)
	printRuntime(start)

if __name__ == "__main__":
	main()
