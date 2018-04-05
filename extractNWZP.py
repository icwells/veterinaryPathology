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

def getDescription(loc, typ, infile, outfile):
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
						res = parseLine(loc, typ, age, sex, digit, splt[1].lower())
						if not res:
							excluded += 1
						elif res.count("NA") < 3:
							found += 1
							output.write(("{},{}\n").format(splt[0], res))
							if res.count("NA") == 1:
								complete += 1
	print(("\tFound data for {} of {} records.").format(found, total))
	print(("\tFound complete information for {} records.").format(complete))
	print(("\tExcluded {} records to account for infant mortaility.\n").format(excluded))

def getTypes():
	# Returns dicts of cancer type and loaction
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

def main():
	parser = ArgumentParser(description = "This script will extract \
age, sex, and diagnosis from NWZP records")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Output file.")
	args = parser.parse_args()
	if not os.path.isfile(args.i):
		print("\n\t[Error] Input file not found. Exiting.\n")
		quit()
	loc, typ = getTypes()
	getDescription(loc, typ, args.i, args.o) 

if __name__ == "__main__":
	main()
