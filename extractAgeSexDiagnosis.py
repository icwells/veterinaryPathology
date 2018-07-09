'''This script will extract age, sex, and diagnosis from a given input file'''

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

def ageInMonths(digit, a):
	# Converts age to months
	d = int(getMatch(digit, a))
	if d == 0:
		return None
	elif "year" in a:
		return d*12
	elif "month" in a:
		return d
	elif "week" in a:
		return d/4
	elif "day" in a:
		return d/30

def infantRecords(line):
	# Identifies infant/neonatal records
	ret = False
	if "infant" in line:
		ret = True
	else:
		match = re.search(r"(peri|neo)nat(e|al)", line)
		if match:
			ret = True
		else:
			match = re.search(r"fet(us|al)", line)
			if match:
				ret = True
	return ret

def parseLine(loc, typ, age, sex, digit, line):
	# Extracts data from line
	l = "NA"
	t = "NA"
	if infantRecords(line) == True:
		# Remove neonatal/infant records
		return None
	a = getMatch(age, line)
	if a != "NA":
		a = ageInMonths(digit, a)
		if not a or a < 0.25:
			# Remove records under 1 week old
			return None
	s = getMatch(sex, line)
	for i in loc:
		x = getMatch(loc[i], line)
		if x != "NA":
			l = i
			break
	for i in typ:
		x = getMatch(typ[i], line)
		if x != "NA":
			t = i
			break
	return ("{},{},{},{}").format(a, s, l, t)

def getDelim(line):
	# Returns delimiter
	for i in ["\t", ",", " "]:
		if i in line:
			return i
	print("\n\t[Error] Cannot determine delimeter. Check file formatting. Exiting.\n")
	quit()	

def getDescription(loc, typ, c, infile, outfile):
	# Reads input file and writes output to file
	total = 0
	found = 0
	excluded = 0
	complete = 0
	first = True
	# Match digits, dash or space, term and any of: "s", dash or space, "old"
	age = re.compile(r"[0-9]+(-|\s)(day|week|month|year)s?(-|\s)(old)?")
	sex = re.compile(r"(fe)?male")
	digit = re.compile(r"[0-9]+")
	print(("\n\tExtracting data from {}...").format(infile))
	with open(outfile, "w") as output:
		output.write("ID,Age(months),Sex,Location,Type\n")
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					total += 1
					if line.strip():
						line = line.strip()
						splt = line.split(delim)
						if len(splt) > c:
							# Compress all fields other than ID into one
							ID = splt[c]
							del splt[c]
							row = " ".join(splt)
							# Skip entries with missing data
							if row != "NA":
								res = parseLine(loc, typ, age, sex, digit, row.lower())
								if not res:
									excluded += 1
								elif res.count("NA") < 3:
									found += 1
									output.write(("{},{}\n").format(ID, res))
									if res.count("NA") == 0:
										complete += 1
				else:
					delim = getDelim(line)
					first = False
	print(("\tFound data for {} of {} records.").format(found, total))
	print(("\tFound complete information for {} records.").format(complete))
	print(("\tExcluded {} records to account for infant mortaility.\n").format(excluded))

def getTypes():
	# Returns dicts of cancer type and loction
	loc = {}
	typ = {}
	with open("cancerdict.tsv", "r") as f:
		for line in f:
			if line.strip() and line.count("\t") >= 2:
				splt = line.strip().split("\t")
				#{location/type: regex}
				if splt[0] == "Location":
					loc[splt[1]] = re.compile(splt[2])
				elif splt[0] == "Type":
					typ[splt[1]] = re.compile(splt[2])				
	return loc, typ

def printError(msg):
	# Prints formatted error message and quits
	print(("\n\t[Error] {}. Exiting.\n").format(msg))
	quit()

def checkArgs(args):
	# Checks args for errors
	if not args.i or not args.o:
		printError("Please specify and input and output file")
	if not os.path.isfile(args.i):
		printError("Input file not found")

def main():
	parser = ArgumentParser(description = "This script will extract \
age, sex, and diagnosis from a given input file")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Output file.")
	parser.add_argument("-c", type = int, default = 0,
help = "ID column number (first column by default).")
	args = parser.parse_args()
	checkArgs(args)
	loc, typ = getTypes()
	getDescription(loc, typ, args.c, args.i, args.o) 

if __name__ == "__main__":
	main()
