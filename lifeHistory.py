'''This script will merge given life history tables.'''

import os
from datetime import datetime
from argparse import ArgumentParser
from unixpath import *
from lhColumns import *
from vetPathUtils import *

def getSpeciesName(c, s):
	# Returns formatted species name
	if "_" in s[c.Species]:
		g, sp = s[c.Species].split("_")
	elif " " in s[c.Species]:
		g, sp = s[c.Species].split()
	else:
		g = s[c.Genus]
		sp = s[c.Species]
	# Get binonial name with first letter in caps
	return g.title() + " " + sp.lower()

def extractTraits(infile, outfile, done):
	# Extracts target traits from input file
	first = True
	total = 0
	count = 0
	updated = 0
	prev = len(done.keys())
	print("\tExtracting traits from input file...")
	with open(outfile, "w") as out:
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					total += 1
					s = line.split(d)
					if len(s) > c.Max:
						species = getSpeciesName(c, s)
						if len(species.split()) == 2:
							if species in done.keys():
								# Update existing missing cells with data from new file
								row, up = c.updateEntry(s, done[species], species)
								out.write((",").join(row) + "\n")
								del done[species]
								if up == True:
									updated += 1
							else:
								# Format new entry
								row = c.formatLine(s, species)
								if row.count("NA") < len(row)-2:
									out.write((",").join(row) + "\n")
									count += 1
				else:
					d = getDelim(line)
					c = LHcolumns(line.split(d), infile)
					first = False
					out.write("Species,FemaleMaturity(months),MaleMaturity(months),Gestation/Incubation(months),\
Weaning(months),Litter/ClutchSize,LittersPerYear,InterbirthInterval,BirthWeight(g),WeaningWeight(g),\
AdultWeight(g),GrowthRate(1/days),MaximumLongevity(months),MetabolicRate(W),Source\n")
		for i in done.keys():
			# Print unmatched previous entries
			out.write(("{},{}\n").format(i, (",").join(done[i])))
	print(("\tExtracted traits for {} species from {} total entries.").format(count, total))
	print(("\tUpdated {} of {} existing entries.").format(updated, prev))

def checkOutput(outfile):
	# Makes new ouput file or reads species from existing file
	done = {}
	first = True
	print("\n\tChecking for previous output...")
	if os.path.isfile(outfile):
		with open(outfile, "r") as f:
			for line in f:
				if first == False:
					s = line.strip().split(",")
					done[s[0]] = s[1:]
				else:
					first = False
		print(("\tFound entries from {} species.").format(len(done.keys())))
	return done

def checkArgs(args):
	if not args.i or not args.o:
		print("\n\t[Error] Please specify an input and output file. Exiting.\n")
		quit()
	checkFile(args.i)

def main():
	start = datetime.now()
	parser = ArgumentParser("This script will extract data from given life history tables.")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Path to output csv. Output will be appended to existing file.")
	args = parser.parse_args()
	checkArgs(args)
	done = checkOutput(args.o)
	extractTraits(args.i, args.o, done)
	printRuntime(start)

if __name__ == "__main__":
	main()
