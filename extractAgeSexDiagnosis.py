'''This script will extract age, sex, and diagnosis from a given input file'''

import os
import re
from argparse import ArgumentParser
from vetPathUtils import getDelim, printError
from unixpath import *

class Matcher():

	def __init__(self):
		# Defines class for handling regex matches for vet oncology data
		self.Location = {}
		self.Type = {}
		self.Infant = re.compile(r"infant|(peri|neo)nat(e|al)|fet(us|al)")
		self.Digit = re.compile(r"[0-9]+")
		# Match digits, dash or space, term and any of: "s", dash or space, "old"
		self.Age = re.compile(r"[0-9]+(-|\s)(day|week|month|year)s?(-|\s)(old)?")
		self.Sex = re.compile(r"(fe)?male")
		self.Necropsy = re.compile(r"necropsy|decesed|cause of death")
		self.Metastasis = re.compile(r"metastatis|mets")
		self.Castrated = re.compile(r"castrat(ed)?|neuter(ed)?|spay(ed)?")
		self.Primary = re.compile(r"primary|single|solitary|source")
		self.__setTypes__()

	def __setTypes__(self):
		# Assigns dicts of cancer type and loction
		with open("cancerdict.tsv", "r") as f:
			for line in f:
				if line.strip() and line.count("\t") >= 2:
					splt = line.strip().split("\t")
					#{location/type: regex}
					if splt[0] == "Location":
						self.Location[splt[1]] = re.compile(splt[2])
					elif splt[0] == "Type":
						self.Type[splt[1]] = re.compile(splt[2])

	def getMatch(self, query, line):
		# Searches line for regular expression
		match = re.search(query, line)
		if match:
			return match.group(0)
		else:
			return "NA"

	def ageInMonths(self, a):
		# Converts age to months
		d = int(self.getMatch(self.Digit, a))
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

	def infantRecords(self, line):
		# Returns True if record os for an infant
		match = re.search(self.Infant, line)
		if match:
			return True
		else:
			return False

	def parseLine(self, line):
		# Extracts data from line
		row = []
		line = line.lower().strip()
		if self.infantRecords(line) == True:
			# Remove neonatal/infant records
			return None
		a = self.getMatch(self.Age, line)
		if a != "NA":
			a = self.ageInMonths(a)
			if not a or a < 0.25:
				# Remove records under 1 week old
				return None
		row.append(str(a))
		row.append(self.getMatch(self.Sex, line))
		for c in [self.Castrated, self.Location, self.Type, self.Primary, self.Metastasis, self.Necropsy]:
			m = "NA"
			if c == self.Location or c == self.Type:
				# Search location/type dicts
				for i in c.keys():
					match = self.getMatch(c[i], line)
					if match != "NA":
						m = i
						break
			else:
				# Search for yes/no matches
				match = self.getMatch(c, line)
				if match != "NA":
					m = "Y"
			row.append(m)
		return ",".join(row)

#-----------------------------------------------------------------------------

def getDescription(infile, outfile, c):
	# Reads input file and writes output to file
	total = 0
	found = 0
	excluded = 0
	complete = 0
	first = True
	matcher = Matcher()
	print(("\n\tExtracting data from {}...").format(infile))
	with open(outfile, "w") as output:
		output.write("ID,Age(months),Sex,Castrated,Location,Type,PrimaryTumor,Metastasis,Necropsy\n")
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					total += 1
					if line.strip():
						splt = line.split(delim)
						if len(splt) > c:
							# Compress all fields other than ID into one
							ID = splt[c]
							del splt[c]
							row = " ".join(splt)
							# Skip entries with missing data
							if row != "NA":
								res = matcher.parseLine(row)
								if not res:
									excluded += 1
								elif res.count("NA") < 8:
									found += 1
									output.write(("{},{}\n").format(ID, res))
									if res.count("NA") == 0:
										complete += 1
				else:
					delim = getDelim(line)
					first = False
	print(("\tFound data for {:,} of {:,} records.").format(found, total))
	print(("\tFound complete information for {:,} records.").format(complete))
	print(("\tExcluded {:,} records to account for infant mortality.\n").format(excluded))

def checkArgs(args):
	# Checks args for errors
	if not args.i or not args.o:
		printError("Please specify and input and output file")
	checkFile(args.i)
	checkFile("cancerdict.tsv")

def main():
	parser = ArgumentParser(description = "This script will extract \
age, sex, and diagnosis from a given input file")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Output file.")
	parser.add_argument("-c", type = int, default = 0,
help = "ID column number (first column by default).")
	args = parser.parse_args()
	checkArgs(args)
	getDescription(args.i, args.o, args.c) 

if __name__ == "__main__":
	main()
