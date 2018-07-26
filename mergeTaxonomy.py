'''This script will concatenate a given database with Kestrel taxonomy results and diagnosis records'''

import os
from datetime import datetime
from argparse import ArgumentParser
from vetPathUtils import printError, getDelim

def printTotal(count, total):
	# Prints number of taxonomies found
	print(("\tFound taxonomies for {} of {} entries.").format(count, total))

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
				total += 1
				if first == False:
					r = ["NA","NA","NA","NA","NA"]
					line = line.strip().split(",")
					if len(line) >= 7:
						if rec:
							if line[0] in rec.keys():
								# Get age, sex, location, and type
								r = rec[line[0]]
						row = formatRow(c, taxa, line, r)
						if row:
							output.write(",".join(row) + "\n")
							count += 1
				else:
					output.write("ID,CommonName,ScientificName,Kingdom,Phylum,Class,Order,Family,Genus,\
Age(months),Sex,Location,CancerType,Necropsy,Code,Diagnosis,Case,Patient#,DateRcvd,Client,Account\n")
					first = False
	printTotal(count, total)

def sortZEPS(taxa, infile, outfile):
	# Sorts database and writes out relevant data with taxonomy
	first = True
	count = 0
	total = 0
	print("\n\tMerging ZEPS taxonomy data...")
	with open(outfile, "w") as output:
		with open(infile, "r") as f:
			for line in f:
				total += 1
				if first == False:
					line = line.strip().split(delim)
					if len(line) == 6:
						n = line[2]
						if n in taxa.keys():
							row = line[:3] + [taxa[n][-1]] + taxa[n][:-1] + line[3:]
							if row:
								output.write(",".join(row) + "\n")
								count += 1
				else:
					output.write("Access#,Category,Breed,ScientificName,Kingdom,\
Phylum,Class,Order,Family,Genus,Sex,Age,Diagnosis\n")
					if "\t" in line:
						delim = "\t"
					else:
						delim = ","
					first = False
	printTotal(count, total)

def sortMSU(taxa, infile, outfile):
	# Sorts database and writes out relevant data with taxonomy
	first = True
	count = 0
	total = 0
	print("\n\tMerging MSU taxonomy data...")
	with open(outfile, "w") as output:
		with open(infile, "r") as f:
			for line in f:
				total += 1
				if first == False:
					line = line.strip().split(delim)
					if len(line) >= 6:
						n = line[5]
						if n in taxa.keys():
							row = line[:6] + [taxa[n][-1]] + taxa[n][:-1] + line[6:]
							if row:
								output.write(",".join(row) + "\n")
								count += 1
				else:
					output.write("ID,Date,Owner,Name,Species,Breed,ScientificName,\
Kingdom,Phylum,Class,Order,Family,Genus,Days,Age,Sex,Diagnosis\n")
					delim = getDelim(line)
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
	print(("\tFound {} taxonomies with {} unique species.").format(len(taxa.keys()), len(species)))
	return taxa

def checkArgs(args):
	# Checks args for errors
	if not args.o:
		printError("Please specify an output file")
	if not args.t:
		printError("Please specify a taxonomy file")
	if not os.path.isfile(args.t):
		printError(("Cannot find {}").format(args.t))
	if args.n:
		if args.m or args.z:
			printError("Please specify only one input file")
		if not os.path.isfile(args.n):
			printError(("Cannot find {}").format(args.n))
		if args.r and not os.path.isfile(args.r):
			printError(("Cannot find {}").format(args.r))
	elif args.m:
		if args.z:
			printError("Please specify only one input file")
		if not os.path.isfile(args.m):
			printError(("Cannot find {}").format(args.m))
	elif args.z:
		if not os.path.isfile(args.z):
			printError(("Cannot find {}").format(args.z))

def main():
	start = datetime.now()
	parser = ArgumentParser("This script will concatenate a given \
database with Kestrel taxonomy results and diagnosis records.")
	parser.add_argument("--cancer", action = "store_true", default = False,
help = "Only extracts and concatenates cancer records (NWZP only; extracts all records by default).")
	parser.add_argument("-n", help = "Path to NWZP file (utf-8 encoded).")
	parser.add_argument("-m", help = "Path to MSU file (utf-8 encoded).")
	parser.add_argument("-z", help = "Path to ZEPS file (utf-8 encoded).")
	parser.add_argument("-t", help = "Path to taxonomy file.")
	parser.add_argument("-r", default = None,
help = "Path to records file with age, sex, and cancer type (NWZP only; not required).")
	parser.add_argument("-o", help = "Output file.")
	args = parser.parse_args()
	checkArgs(args)
	taxa = getTaxa(args.t)
	if args.n:
		if args.r:
			rec = getRecords(args.r)
		sortNWZP(args.cancer, taxa, rec, args.n, args.o)
	elif args.m:
		sortMSU(taxa, args.m, args.o)
	elif args.z:
		sortZEPS(taxa, args.z, args.o)
	print(("\n\tFinished. Runtime: {}\n").format(datetime.now() - start))

if __name__ == "__main__":
	main()
