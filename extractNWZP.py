'''This script will extract age, sex, and diagnosis from NWZP records'''

import os
import re
from argparse import ArgumentParser

def parseLine(age, sex, line):
	# Extracts data from line
	a = "NA"
	s = "NA"
	d = "NA"
	match = re.search(age, line)
	if match:
		print(line, match.group)
		quit()
	# Search for sex
	splt = line.split()
	for i in splt:
		if re.search(sex, i) == True:
			s = i
			break
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
				if first == False and line.strip():
					try:
						line = line.strip()
						splt = line.split("\t")
						print(line)
						if len(splt) > 2:
							# Compress all fields other than ID into one
							splt[1] = " ".join(splt[1:])
						# Skip entries with missing data
						if splt[1] != "NA":
							res = parseLine(age, sex, splt[1].lower())
							if res:
								found += 1
								output.write(("{},{}\n").format(splt[0], res))
					except UnicodeEncodeError:
						pass
				else:
					first = True
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
