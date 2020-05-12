'''Splits comments column for checking diagnoses'''

from argparse import ArgumentParser
from datetime import datetime
import os
import pandas as pd
import unixpath

class Splitter():

	def __init__(self, args):
		unixpath.checkFile(args.i)
		self.comments = set()
		self.diag = {}
		self.header = {}
		self.infile = args.i
		self.outfile = args.o
		self.__readInfile__()
		self.__writeFile__()

	def __writeFile__(self):
		# Writes diag and comments to seperate xlsx sheets
		c = pd.DataFrame(list(self.comments))
		d = []
		for k in self.diag.keys():
			for i in self.diag[k]:
				d.append([k, i])
		df = pd.DataFrame(d, columns = ["Location", "Type"])
		with pd.ExcelWriter(self.outfile) as writer:
			df.to_excel(writer, sheet_name = "Diagnoses")
			c.to_excel(writer, sheet_name = "Comments")

	def __setHeader__(self, row):
		# Stores header line and indeces in dict
		for idx, i in enumerate(row):
			self.header[i] = idx

	def __parseLine__(self, row):
		# Stores diagnoses and comments
		l = row[self.header["Location"]]
		t = row[self.header["Type"]]
		c = row[self.header["Comments"]]
		if l != "NA" and t != "NA":
			if l not in self.diag.keys():
				self.diag[l] = set()
			self.diag[l].add(t)
		for i in c.split(";"):
			i = i.strip()
			if len(i) > 4:
				self.comments.add(i)

	def __readInfile__(self):
		# Reads diagnosis data into class
		first = True
		with open(self.infile, "r") as f:
			for line in f:
				line = line.strip()
				if not first:
					self.__parseLine__(line.split(d))
				else:
					d = unixpath.getDelim(line)
					self.__setHeader__(line.split(d))
					first = False

def main():
	start = datetime.now()
	parser = ArgumentParser("Splits comments column for checking diagnoses.")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Path to output file.")
	Splitter(parser.parse_args())
	print(("\tTotal runtime: {}\n").format(datetime.now() - start))

if __name__ == "__main__":
	main()
