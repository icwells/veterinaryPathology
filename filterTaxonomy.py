'''Updates Kestrel taxonomy file by replacing exiting taxonomies with new taxonomies and deleting entries with no taxonomies.'''

from argparse import ArgumentParser
from datetime import datetime
import os
import unixpath
from vetPathUtils import *

class TaxaUpdater():

	def __init__(self, args):
		self.infile = args.i
		self.taxafile = args.t
		self.outfile = args.o
		self.delete = set()
		self.new = {}
		self.updated = set()
		for i in [self.infile, self.taxafile]:
			unixpath.checkfile(i)
		self.__setTaxa__()

	def __setTaxa__(self):
		# Reads in updated taxonomies
		first = True
		with open(self.infile, "r") as f:
			for line in f:
				line = line.strip()
				if first == False:
					row = line.split(d)
					if len(row) > 2:
						self.new[row[0]] = row
					else:
						self.delete.add(row[0])
				else:
					d = getDelim(line)
					first = False

	def updateTaxa(self):
		# Updates taxa file
		first = True
		with open(self.outfile, "w") as out:
			with open(self.taxafile, "r") as f:
				for line in f:
					line = line.strip()
					if first == False:

					else:
					d = getDelim(line)
					c = Columns(line.split(d))
					first = False

def main():
	start = datetime.now()
	parser = ArgumentParser("Updates Kestrel taxonomy file by replacing exiting taxonomies with new taxonomies and deleting entries with no taxonomies.")
	parser.add_argument("-t", help = "Path to Kestrel taxonomy file.")
	parser.add_argument("-i", help = "Path to input file of updated taxonomies.")
	parser.add_argument("-t", help = "Path to output csv.")
	u = TaxaUpdater()(parser.parse_args())
	u.updateTaxa()
	printRuntime(start))

if __name__ == "__main__":
	main()
