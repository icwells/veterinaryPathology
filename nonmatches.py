'''Prints csv of records which did not have a malignant match.'''

import os
from datetime import datetime
from argparse import ArgumentParser
from vetPathUtils import *
from unixpath import *

def getUnmatched(ids, infile, outfile):
	# Writes unmatched records to file
	first = True
	total = 0
	count = 0
	print("\tIdentifying records with no malignancy infomation...")
	with open(outfile, "w") as out:
		out.write("ID,Code,Diagnosis\n")
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					total += 1
					line = line.strip().split(d)
					if line[0] not in ids:
						out.write(("{},{},{}\n").format(line[0], line[c.Code], line[c.Comments]))
						count += 1
				else:
					d = getDelim(line)
					c = Columns(line.split(d))
					first = False
	print(("\tFound {:,} records with no malignancy information out of {:,} total.").format(count, total))

def getMalignancy(infile):
	# Returns set of ids which have malignancy info present
	ret = set()
	first = True
	print("\n\tReading diagnosis info...")
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				line = line.strip().split(d)
				if line[c.Malignant] != "NA":
					ret.add(line[0])
			else:
				d = getDelim(line)
				c = Columns(line.split(d))
				first = False
	return ret

def checkArgs(args):
	# Checks input files
	for i in [args.i, args.d, args.o]:
		if not i:
			printError("Please provide input, output, and diagnosis files")
	for i in [args.i, args.d]:
		checkFile(i)
	return args

def main():
	start = datetime.now()
	parser = ArgumentParser("Prints csv of records which did not have a malignant match.")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-d", help = "Path to diagnosis file.")
	parser.add_argument("-o", help = "Path to output file.")
	args = checkArgs(parser.parse_args())
	ids = getMalignancy(args.d)
	getUnmatched(ids, args.i, args.o)
	printRuntime(start)

if __name__ == "__main__":
	main()
