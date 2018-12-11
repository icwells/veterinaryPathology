'''Merges manually curated taxonomies and prints out kestrel search input file with curator name.'''

import os
from argparse import ArgumentParser
from glob import glob
from unixpath import *

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

class Queries():
	def __init__(self, outdir):
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
		end = min(len(row), self.header.corrected)
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

	def writeTaxa(self):
		# Writes queries dict ot file
		count = 0
		print(("\tWriting taxonomies to {}").format(self.taxaout))
		with open(self.taxaout, "w") as out:
			out.write(self.theader)
			for i in self.taxonomy.keys():
				out.write(("{},{}\n").format(i, ",".join(self.taxonomy[i])))
				count += 1
		print(("\tIdentified {:,} passing taxonomies from {:,} total records.").format(count, self.total))

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

def main():
	parser = ArgumentParser(
"Merges manually curated taxonomies and prints out kestrel search input file with curator name.")
	parser.add_argument("-i", help = "Input directory of csv files (file anmes are assumed to be <name_of_curator>.csv.")
	parser.add_argument("-o", help = "Path to output directory.")
	args = parser.parse_args()
	args.i = checkDir(args.i)
	args.o = checkDir(args.o, True)
	mergeTaxa(args.i, args.o)
	print("\tFinished.\n")

if __name__ == "__main__":
	main()
