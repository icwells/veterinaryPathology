'''This script will merge given life history tables.'''

import os
from datetime import datetime
from argparse import ArgumentParser
from unixpath import *
from vetPathUtils import *

def extractTraits(infile, outfile, done):
	# Extracts target traits from input file
	first = True
	total = 0
	count = 0
	print("\nExtracting traits from input file...")
	with open(outfile, "w") as out:
		with open(infile, "r") as f:
			for line in f:
				if first == False:

				else:
					d = getDelim(line)
					c = LHcolumns(line.split(d), infile)
					first = False
	print(("Extracted traits for {} species from {} total entries.").format(count, total))

def checkOutput(outfile):
	# Makes new ouput file or reads species from existing file
	out = []
	first = True
	if os.path.isfile(outfile):
		print("\n\tGetting previous output...")
		with open(outfile, "r") as f:
			if first == False:
				done.append(line.split(",")[0])
			else:
				first = False
		print(("\tFound entries from {} species.").format(len(done)))
	else:
		print("\n\tInitializing output file...")
		with open(outfile, "w") as out:
			out.write("Species,FemaleMaturity(days),MaleMaturity(days),Gestation/Incubation(days),\
Weaning(days),Litter/ClutchSize,LittersPerYear,InterbirthInterval,BirthWeight(g),WeaningWeight(g),\
AdultWeight(g),GrowthRate(1/days),MaximumLongevity(yrs),MetabolicRate(W),Source\n")
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
