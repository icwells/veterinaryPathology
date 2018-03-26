'''This script will concatenate the MSU database with Kestrel taxonomy results'''

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
					line = line.replace(",", "")
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
Kingdom,Phylum,Order,Class,Family,Genus,Days,Age,Sex,Diagnosis\n")
					delim = ","
					if "\t" in line:
						delim = "\t"
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
the MSU database with Kestrel taxonomy results.")
	parser.add_argument("-i", help = "Path to MSU database file.")
	parser.add_argument("-t", help = "Path to taxonomy file.")
	parser.add_argument("-o", help = "Output file.")
	args = parser.parse_args()
	taxa = getTaxa(args.t)
	sortDB(taxa, args.i, args.o)

if __name__ == "__main__":
	main()
