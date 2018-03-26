'''This script will concatenate the ZEPS database with Kestrel taxonomy results'''

import argparse

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
Phylum,Order,Class,Family,Genus,Sex,Age,Diagnosis\n")
					if "\t" in line:
						delim = "\t"
					else:
						delim = ","
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
the ZEPS database with Kestrel taxonomy results.")
	parser.add_argument("-i", help = "Path to ZEPS file.")
	parser.add_argument("-t", help = "Path to taxonomy file.")
	parser.add_argument("-o", help = "Output file.")
	args = parser.parse_args()
	taxa = getTaxa(args.t)
	sortDB(taxa, args.i, args.o)

if __name__ == "__main__":
	main()
