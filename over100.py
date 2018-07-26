'''This script will extract summary data for species at least 100 records'''

from argparse import ArgumentParser
from unixpath import *
from vetPathUtils import *

def getTotals(infile):
	# Returns list of species with at least 100 entries
	totals = {}
	first = True
	with open(infile, "r") as f:
		for line in f:
			if first == False:


			else:
				

def checkArgs(args):
	# Check args for errors
	if not args.i or not args.o:
		printError("Please specify input and output files")
	if not os.path.isfile(args.i):
		printError(("Cannot find {}").format(args.i))

def main():
	parser = ArgumentParser(
"This script will extract summary data for species at least 100 records.")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Path to output file.")
	args = parser.parse_args()
	checkArgs(args)
	counts = getTotals(args.i)

if __name__ == "__main__":
	main()
