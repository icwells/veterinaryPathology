'''Filters duplicate records from input files'''

import os
from datetime import datetime
from argparse import ArgumentParser
from vetPathUtils import *
from records import RepeatIdentifier, Record
from summarizeRates import checkArgs

class DuplicateFilter():

	def __init__(self, infile, outfile):
		self.infile = infile
		self.outfile = outfile
		self.reps = RepeatIdentifier()
		self.header = ""
		self.d = ""
		self.col = None
		self.total = 0
		self.dups = {}

	def __parseHeader__(self, line):
		# Store delimiter and column info
		self.header = line
		self.d = getDelim(line)
		self.col = Columns(line.split(self.d))

	def writeDuplicates(self, out):
		# Writes passing duplicate records to output file
		print("\tResolving duplicate records...")
		ids = self.reps.getSourceIDs()
		for i in ids:
			out.write(self.dups[i])		
		print(("\tWrote {:,} duplicate records from a total of {:,} duplicates.").format(len(ids), len(self.reps.ids)))		

	def checkDuplicates(self, line):
		# Returns true for unique records, stores duplicates
		ret = True
		cancer = False
		s = line.strip().split(self.d)
		if self.col.Patient and s[self.col.Patient] in self.reps.ids:
			if self.col.Code and "8" in s[self.col.Code]:
				cancer = True
			# Sort duplicates and store for later
			rec = Record(s[self.col.Sex], s[self.col.Age], s[self.col.Patient], s[self.col.Species], cancer, s[self.col.ID])
			self.reps.sortReplicates(rec)
			self.dups[s[self.col.ID]] = line
			ret = False
		return ret

	def removeDuplicates(self):
		# Writes non-duplicate records to file
		first = True
		count = 0
		print("\tFiltering duplicate records...")
		with open(self.outfile, "w") as out:
			out.write(self.header + "\n")
			with open(self.infile, "r") as f:
				for line in f:
					if first == False:
						write = self.checkDuplicates(line)
						if write == True:
							count += 1
							out.write(line)
					else:
						first = False
			print(("\tWrote {:,} unique records from a total of {:,} records.").format(count, self.total))
			self.writeDuplicates(out)

	def setDuplicates(self):
		# Identifies duplicate entries
		first = True
		print("\n\tIdentifying duplicate records...")
		with open(self.infile, "r") as f:
			for line in f:
				line = line.strip()
				if first == False:
					s = line.split(self.d)
					self.total += 1
					if self.col.Account and self.col.Patient and self.col.Max < len(s):
						# Record account and patient names
						self.reps.add(s[self.col.Patient], s[self.col.Account])
				else:
					self.__parseHeader__(line)					
					first = False
		self.reps.setReplicates()

def main():
	start = datetime.now()
	parser = ArgumentParser("Filters duplicate records from input files.")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Path to output csv.")
	args = parser.parse_args()
	checkArgs(args)
	f = DuplicateFilter(args.i, args.o)
	f.setDuplicates()
	f.removeDuplicates()
	printRuntime(start)

if __name__ == "__main__":
	main()
