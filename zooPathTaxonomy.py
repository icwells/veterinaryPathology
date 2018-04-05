'''This script will concatenate the NWZP database with Kestrel taxonomy results'''

import argparse

def formatFullData(c, taxa, line, r):
	# Formats line from fulldata file
	row = []
	if c == True:
		if "8" not in line[8]:
			# Skip non-cancer records
			return None 
	n = line[6].replace(",", " ")
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

def formatMasterFile(c, taxa, line, r):
	# Formats line from master file
	row = []
	if c == True:
		if "8" not in line[6]:
			# Skip non-cancer records
			return None 
	n = line[4].replace(",", " ")
	if n in taxa.keys():
		# ID, common, and scientific names
		row = [line[0], n, taxa[n][-1]]
		for i in taxa[n][:-1]:
			# Append remainder of taxonomy
			row.append(i)
		row.extend(r)
		# Add remaining data from database
		row.extend([line[6].replace(",",";"), line[7].replace(",",";"), 
					line[2], line[5], line[3], line[0], line[1]])
	return row

def sortDB(c, taxa, rec, infile, outfile):
	# Sorts database and writes out relevant data with taxonomy
	fd = True
	first = True
	count = 0
	total = 0
	with open(outfile, "w", errors="surrogateescape") as output:
		with open(infile, "r", errors="surrogateescape") as f:
			for line in f:
				total += 1
				if first == False:
					r = ["NA","NA","NA","NA"]
					line = line.strip().split("\t")
					if len(line) > 7:
						if rec:
							if line[0] in rec.keys():
								# Get age, sex, location, and type
								r = rec[line[0]]
						if fd == True:
							row = formatFullData(c, taxa, line, r)
						else:
							row = formatMasterFile(c, taxa, line, r)
						if row:
							output.write(",".join(row) + "\n")
							count += 1
				else:
					output.write("ID,CommonName,ScientificName,Kingdom,Phylum,Order,Class,Family,Genus,\
Age(months),Sex,Location,CancerType,Code,Diagnosis,Case,Patient#,DateRcvd,Client,Account\n")
					if len(line.split(",")) == 9:
						# Sort data from masterfile instead of fulldata
						fd = False
					first = False
	print(("\n\tFound taxonomies for {} of {} entries.\n").format(count, total))

def getRecords(infile):
	# Reads in dictionary of age, sex, and cancer type
	first = True
	rec = {}
	if infile:
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					line = line.strip().split(",")
					# {ID: [age, sex, type]}
					rec[line[0]] = line[1:]
				else:
					first = False
		return rec
	else:
		return None

def getTaxa(infile):
	# Reads in taxonomy dictionary
	first = True
	taxa = {}
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				line = line.split(",")
				# Query name: [taxonomy] (drops search term and urls)
				taxa[line[0]] = line[2:9]
			else:
				first = False
	return taxa

def main():
	parser = argparse.ArgumentParser(description = "This script will concatenate \
the NWZP database with Kestrel taxonomy results.")
	parser.add_argument("--cancer", action = "store_true", default = False,
help = "Only extracts and concatenates cancer records (extracts all records by default).")
	parser.add_argument("-i", help = "Path to NWZP file.")
	parser.add_argument("-t", help = "Path to taxonomy file.")
	parser.add_argument("-r", default = None,
help = "Path to records file with age, sex, and cancer type (not required).")
	parser.add_argument("-o", help = "Output file.")
	args = parser.parse_args()
	taxa = getTaxa(args.t)
	rec = getRecords(args.r)
	sortDB(args.cancer, taxa, rec, args.i, args.o)

if __name__ == "__main__":
	main()
