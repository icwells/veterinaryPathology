'''Merges manually curated taxonomies and prints out kestrel search input file with curator name.'''

import os
from datetime import datetime
from argparse import ArgumentParser
from glob import glob
from unixpath import *
from vetPathUtils import printRuntime

class Header():
	def __init__(self, row):
		self.query = -1
		self.species = -1
		self.corrected = -1
		self.__setColumns__(row)

	def __setColumns__(self, row):
		# Store row indeces
		for idx, i in enumerate(row):
			i = i.strip()
			if i == "Query":
				self.query = idx
			elif i == "Species":
				self.species = idx
			elif "Corrected Species" in i:
				self.corrected = idx
				break

#-------------------------------------------------------------------------------

class Queries():
	def __init__(self, outdir=""):
		self.qheader = "Query,SearchTerm,Type,Name\n"
		self.queryout = outdir + "searchTerms.csv"
		self.theader = ""
		self.taxaout = outdir + "taxonomy.csv"
		self.header = None
		self.delim = None
		self.queries = {}
		self.taxonomy = {}
		self.total = 0

	def __addTaxa__(self, row, name):
		# Adds taxonomy to dict
		end = min(len(row), self.header.corrected, 15)
		self.taxonomy[row[0]] = row[1:end]
		self.taxonomy[row[0]].append(name)

	def __checkEntry__(self, s, name):
		# Adds data from row to appropriate dict
		if len(s) > self.header.corrected and len(s[self.header.corrected]) >= 2:
			# Check corrected entry
			if "?" not in s[self.header.corrected]:
				# Skip unintelligable entries
				spl = s[self.header.corrected].split()
				if len(spl) != 2:
					sp = " ".join(spl[:2])
				else:
					sp = s[self.header.corrected]
				# Add corrected scientific name
				self.queries[s[self.header.query]] = [sp, name]
		else:
			# Check existing scientific name
			spl = s[self.header.species].split()
			if len(spl) >= 2:
				sp = spl[1].strip().lower()
				if sp == "sp." or sp == "na":
					# Add entries with missing species data to queries
					self.queries[s[self.header.query]] = [s[self.header.species], name]
				else:
					# Keep well formatted names
					self.__addTaxa__(s, name)
			else:
				# Add malformed entries to queries
				self.queries[s[self.header.query]] = [s[self.header.species], name]

	def readCSV(self, infile):
		# Reads csv into dict
		first = True
		name = getFileName(infile)
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					self.total += 1
					s = line.strip().split(self.delim)
					self.__checkEntry__(s, name)
				else:
					if self.delim is None:
						self.delim = getDelim(line)
						row = line.split(self.delim)
						self.header = Header(row)
						row = row[:self.header.corrected]
						row.append("Name")
						self.theader = ",".join(row) + "\n"
					first = False

	def checkOutput(self):
		# Stores set of curated queries
		self.queries = set()
		first = True
		with open(self.taxaout, "r") as f:
			for line in f:
				if first == False:
					s = line.split(",")
					self.queries.add(s[0])
				else:
					first = False

	def addEntries(self, infile):
		# Stores well formed taxonomies not present in curated file
		first = True
		with open(infile, "r") as f:
			for line in f:
				s = line.strip().split(",")
				if first == False:
					self.total += 1
					if s[0] not in self.queries:
						if s[2:self.header.species+1].count("NA") <=1:
							spl = s[self.header.species].split()
							if 2 <= len(spl) <= 3 and spl[1].strip().lower() != "sp.":
								# Only use unique entires with no more than one NA and bi/trinomial name present
								self.__addTaxa__(s, "NA")
				else:
					# Store header values to use the add method
					self.header = Header(s)
					self.header.corrected = len(s) + 1
					first = False

	def appendCurator(self, infile):
		# Appends curator names to kestrel taxonomies
		first = True
		with open(infile, "r") as f:
			for line in f:
				s = line.strip().split(",")
				if first == False:
					name = "NA"
					if s[0] in self.queries.keys():
						name = self.queries[s[0]]
					self.__addTaxa__(s, name)
					self.total += 1
				else:
					# Store header values to use the add method
					self.header = Header(s)
					self.header.corrected = len(s) + 1
					first = False

	def getCurators(self):
		# Gets dict from search term file
		first = True
		with open(self.queryout, "r") as f:
			for line in f:
				if first == False:
					s = line.strip().split(",")
					# Store in queries dict
					self.queries[s[0]] = s[3]
				else:
					first = False

	def writeQueries(self):
		# Writes queries dict ot file
		count = 0
		print(("\tWriting queries to {}").format(self.queryout))
		with open(self.queryout, "w") as out:
			out.write(self.qheader)
			for i in self.queries.keys():
				row = ",".join([i, self.queries[i][0], "scientific", self.queries[i][1]])
				out.write(row + "\n")
				count += 1
		print(("\tIdentified {:,} corrections from {:,} total records.").format(count, self.total))

	def writeTaxa(self, append = False):
		# Writes queries dict ot file
		count = 0
		mode = "w"
		if append == True:
			mode = "a"
		print(("\tWriting taxonomies to {}").format(self.taxaout))
		with open(self.taxaout, mode) as out:
			if append == False:
				out.write(self.theader)
			for i in self.taxonomy.keys():
				out.write(("{},{}\n").format(i, ",".join(self.taxonomy[i])))
				count += 1
		print(("\tIdentified {:,} passing taxonomies from {:,} total records.").format(count, self.total))

#-----------------------------------------------------------------------------

def mergeTaxa(indir, outdir):
	# Reads each csv and adds to dict
	infiles = glob(indir + "*.csv")
	q = Queries(outdir)
	print(("\n\tIdentified {} files.").format(len(infiles)))
	for i in infiles:
		print(("\tReading {}").format(i))
		q.readCSV(i)
	q.writeQueries()
	q.writeTaxa()

def appendTaxa(infile, outdir):
	# Appends curator name to ketrel search output and concatenates with original taxonomy
	q = Queries(outdir)
	print("\n\tMerging taxonomy data...")
	q.getCurators()
	q.appendCurator(infile)
	q.writeTaxa(True)

def fillTaxa(infile, outfile):
	# Adds missing taxonomies which are not malformed to outfile
	q = Queries()
	q.taxaout = outfile
	print("\n\tAdding missing taxonomies...")
	q.checkOutput()
	q.addEntries(infile)
	q.writeTaxa(True)

def checkArgs(args):
	# Checks for errors
	if args.merge == True and args.fill == True:
		printError("Please specify only one run mode")
	if args.merge == False and args.fill == False:
		args.i = checkDir(args.i)
	else:
		checkFile(args.i)
	if args.fill == False:
		args.o = checkDir(args.o, True)
	else:
		checkFile(args.o)
	return args

def main():
	start = datetime.now()
	parser = ArgumentParser(
"Merges manually curated taxonomies and prints out kestrel search input file with curator name.")
	parser.add_argument("--merge", action = "store_true", default = False, help = "Merges kestrel output (given with -i)\
 with curator names from search file and appends to output taxonomy file (directory given with -o).")
	parser.add_argument("--fill", action = "store_true", default = False,
help = "Fill in missed taxonomies from original taxonomy file (given with -i).")
	parser.add_argument("-i", help = "Input directory of csv files (file names are assumed to be <name_of_curator>.csv.")
	parser.add_argument("-o", help = "Path to output file/directory.")
	args = checkArgs(parser.parse_args())
	if args.fill == True:
		fillTaxa(args.i, args.o)
	elif args.merge == True:
		appendTaxa(args.i, args.o)
	else:
		mergeTaxa(args.i, args.o)
	printRuntime(start)

if __name__ == "__main__":
	main()
