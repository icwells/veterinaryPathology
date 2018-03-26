'''This script will concatenate the NWZP database with Kestrel taxonomy results'''

import argparse

def formatFullData(taxa, line):
	# Formats line from fulldata file
	row = []
	n = line[6].replace(",", " ")
	if n in taxa.keys():
		# Common and scientific names
		row = [n, taxa[n][-1]]
		for i in taxa[n][:-1]:
			# Append remainder of taxonomy
			row.append(i)
		# Add remaining data from database
		row.extend([line[7].replace(",",";"), line[8].replace(",",";"), 
					line[3], line[7], line[5], line[1], line[2]])
	return row

def formatMasterFile(taxa, line):
	# Formats line from master file
	row = []
	n = line[4].replace(",", " ")
	if n in taxa.keys():
		# Common and scientific names
		row = [n, taxa[n][-1]]
		for i in taxa[n][:-1]:
			# Append remainder of taxonomy
			row.append(i)
		# Add remaining data from database
		row.extend([line[6].replace(",",";"), line[7].replace(",",";"), 
					line[2], line[5], line[3], line[0], line[1]])
	return row

def sortDB(taxa, infile, outfile):
	# Sorts database and writes out relevant data with taxonomy
	first = True
	count = 0
	total = 0
	with open(outfile, "w", errors="surrogateescape") as output:
		with open(infile, "r", errors="surrogateescape") as f:
			for line in f:
				total += 1
				if first == False:
					line = line.strip().split("\t")
					if len(line) > 7:
						if fd == True:
							row = formatFullData(taxa, line)
						else:
							row = formatMasterFile(taxa, line)
						if row:
							output.write(",".join(row) + "\n")
							count += 1
				else:
					output.write("CommonName,ScientificName,Kingdom,Phylum,\
Order,Class,Family,Genus,Code,Diagnosis,Case,Patient#,DateRcvd,Client,Account\n")
					if len(line.split(",")) == 9:
						fd = False
					else:
						fd = True
					first = False
	print(("\n\tFound taxonomies for {} of {} entries.\n").format(count, total))	

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
	parser.add_argument("-i", help = "Path to NWZP file.")
	parser.add_argument("-t", help = "Path to taxonomy file.")
	parser.add_argument("-o", help = "Output file.")
	args = parser.parse_args()
	taxa = getTaxa(args.t)
	sortDB(taxa, args.i, args.o)

if __name__ == "__main__":
	main()
