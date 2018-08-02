'''This script will extract age, sex, and diagnosis from a given input file'''

import os
import re
from datetime import datetime
from argparse import ArgumentParser
from copy import deepcopy
from vetPathUtils import *
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
		# Binary expressions
		self.Castrated = re.compile(r"(not )?(castrat(ed)?|neuter(ed)?|spay(ed)?)")
		self.Malignant = re.compile(r"(not )?(malignant|benign)")
		self.Metastasis = re.compile(r"(no )?(metastatis|mets)")
		self.Primary = re.compile(r"primary|single|solitary|source")
		self.Necropsy = re.compile(r"(necropsy|decesed|cause of death)|(biopsy)")
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

	def __getMatch__(self, query, line, subset = True):
		# Searches line for regular expression
		match = re.search(query, line)
		if match:
			if subset == True:
				return match.group(0)
			else:
				return match
		else:
			return "NA"

	def __binaryMatch__(self, query, line, exp = None):
		# Sorts results for yes/no search
		ret = "NA"
		match = self.__getMatch__(query, line, False)
		if match != "NA":
			if exp:
				# Return N if group 2 == exp
				if match.group(2):
					if match.group(1):
						# Store negated value
						if match.group(2) == exp:
							ret = "Y"
						else:
							ret = "N"
					else:
						if match.group(2) == exp:
							ret = "N"
						else:
							ret = "Y"
			else:
				# Return N if no/not was found
				if match.group(1):
					ret = "N"
				elif match.group(2):
					ret = "Y"
		return ret

	def __ageInMonths__(self, a):
		# Converts age to months
		d = int(self.__getMatch__(self.Digit, a))
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

	def __infantRecords__(self, line):
		# Returns True if record os for an infant
		match = re.search(self.Infant, line)
		if match:
			return True
		else:
			return False

	def parseLine(self, line, age, cancer = True):
		# Extracts data from line
		row = []
		line = line.lower().strip()
		if self.__infantRecords__(line) == True:
			a = 0
		elif age:
			a = age
		else:
			a = self.__getMatch__(self.Age, line)
			if a != "NA":
				a = self.__ageInMonths__(a)
		row.append(str(a))
		row.append(self.__getMatch__(self.Sex, line))
		cas = self.__binaryMatch__(self.Castrated, line)
		if cas == "NA" and "intact" in line:
			cas = "N"
		row.append(cas)
		for c in [self.Location, self.Type]:
			m = "NA"
			if cancer == True:
				# Search putative cancer records
				for i in c.keys():
					match = self.__getMatch__(c[i], line)
					if match != "NA":
						m = i
						break
			row.append(m)
		row.append(self.__binaryMatch__(self.Malignant, line, "benign"))
		met = self.__binaryMatch__(self.Metastasis, line)
		if met == "N" and m != "NA":
			# Store yes for primary if a tumor was found but no metastasis
			row.append("Y")
		else:
			if self.__getMatch__(self.Primary, line) != "NA":
				row.append("Y")
			else:
				row.append("NA")
		row.append(met)
		row.append(self.__binaryMatch__(self.Necropsy, line, "biopsy"))
		return ",".join(row)

#-----------------------------------------------------------------------------

def getAge(col, row):
	# Returns age if given
	if col.Days:
		age = row[col.Days]
	elif col.Age:
		age = row[col.Age]
	else: 
		return None
	try:
		age = float(age)
	except ValueError:
		return None
	if col.Days:
		return ("{:.2f}").format(age/30)
	if col.Age:
		return ("{:.2f}").format(age*12)
	

def getDescription(infile, outfile, c):
	# Reads input file and writes output to file
	total = 0
	found = 0
	complete = 0
	first = True
	matcher = Matcher()
	print(("\n\tExtracting data from {}...").format(infile))
	with open(outfile, "w") as output:
		output.write("ID,Age(months),Sex,Castrated,Location,Type,Malignant,PrimaryTumor,Metastasis,Necropsy\n")
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					total += 1
					if line.strip():
						splt = line.split(delim)
						if len(splt) > c:
							# Compress all fields other than ID into one
							ID = splt[c]
							age = getAge(col, line)
							row = deepcopy(splt)
							del row[c]
							row = " ".join(row)
							# Skip entries with missing data
							if row != "NA":
								if col.Service == "NWZP" and "8" not in splt[col.Code]:
									res = matcher.parseLine(row, age, False)
								else:
									res = matcher.parseLine(row, age, True)
								if res.count("NA") < len(res):
									found += 1
									output.write(("{},{}\n").format(ID, res))
									if res.count("NA") == 0:
										complete += 1
				else:
					delim = getDelim(line)
					col = Columns(line.split(delim), getService(infile))
					first = False
	print(("\tFound data for {:,} of {:,} records.").format(found, total))
	print(("\tFound complete information for {:,} records.").format(complete))

def checkArgs(args):
	# Checks args for errors
	if not args.i or not args.o:
		printError("Please specify and input and output file")
	checkFile(args.i)
	checkFile("cancerdict.tsv")

def main():
	start = datetime.now()
	parser = ArgumentParser(description = "This script will extract \
age, sex, and diagnosis from a given input file")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Output file.")
	parser.add_argument("-c", type = int, default = 0,
help = "ID column number (first column by default).")
	args = parser.parse_args()
	checkArgs(args)
	getDescription(args.i, args.o, args.c)
	printRuntime(start)

if __name__ == "__main__":
	main()
