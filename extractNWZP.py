'''This script will extract age, sex, and diagnosis from NWZP records'''

import os
import re
from argparse import ArgumentParser

def getMatch(query, line):
	# Searches line for regular expression
	match = re.search(query, line)
	if match:
		return match.group(0)
	else:
		return "NA"

def parseLine(age, sex, line):
	# Extracts data from line
	a = getMatch(age, line)
	s = getMatch(sex, line)
	d = "NA"
	return ("{},{},{}").format(a, s, d)

def getDescription(infile, outfile):
	# Reads input file and writes output to file
	total = 0
	found = 0
	first = True
	# Match digits, dash or space, term and any of: "s", dash or space, "old"
	age = re.compile(r"[0-9]+(-|\s)(day|week|month|year)s?(-|\s)(old)?")
	sex = re.compile(r"(fe)?male")
	print(("\n\tExtracting data from {}...").format(infile))
	with open(outfile, "w") as output:
		output.write("ID,Age,Sex,Diagnosis\n")
		with open(infile, "r", errors="surrogateescape") as f:
			for line in f:
				total += 1
				if line.strip():
					line = line.strip()
					splt = line.split("\t")
					if len(splt) > 2:
						# Compress all fields other than ID into one
						splt[1] = " ".join(splt[1:])
					# Skip entries with missing data
					if splt[1] != "NA":
						res = parseLine(age, sex, splt[1].lower())
						if res.count("NA") < 3:
							found += 1
							output.write(("{},{}\n").format(splt[0], res))
	print(("\tFound data for {} of {} records.\n").format(found, total))

def main():
	parser = ArgumentParser(description = "This script will extract \
age, sex, and diagnosis from NWZP records")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Output file.")
	args = parser.parse_args()
	if not os.path.isfile(args.i):
		print("\n\t[Error] Input file not found. Exiting.\n")
		quit()
	getDescription(args.i, args.o) 

if __name__ == "__main__":
	main()
