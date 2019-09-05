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
			unixpath.checkFile(i)
		self.__setTaxa__()

	def __setTaxa__(self):
		# Reads in updated taxonomies
		first = True
		print("\n\tReading updated taxonomies...")
		with open(self.infile, "r") as f:
			for line in f:
				line = line.strip()
				if first == False:
					row = line.split(d)
					if row[2].strip():
						self.new[row[0]] = row
					else:
						self.delete.add(row[0])
				else:
					d = getDelim(line)
					first = False

	def updateTaxa(self):
		# Updates taxa file
		first = True
		dlt = 0
		up = 0
		n = 0
		print("\tUpdating taxonomy file...")
		with open(self.outfile, "w") as out:
			with open(self.taxafile, "r") as f:
				for line in f:
					if first == False:
						s = line.split(d)[0]
						if s in self.new.keys():
							# Replace with updated row
							out.write(",".join(self.new[s]) + "\n")
							self.updated.add(s)
							up += 1
						elif s not in self.delete:
							# Keep existing row
							out.write(line)
						else:
							dlt += 1
					else:
						d = getDelim(line.strip())
						first = False
			for i in self.new.keys():
				if i not in self.updated:
					# Write novel entries
					out.write(",".join(self.new[i]) + "\n")
					n += 1
		print(("\tUpdated {} taxonomies.\n\tDeleted {} taxonomies.\n\tAdded {} taxonomies.").format(up, dlt, n))

def main():
	start = datetime.now()
	parser = ArgumentParser("Updates Kestrel taxonomy file by replacing exiting taxonomies with new taxonomies and deleting entries with no taxonomies.")
	parser.add_argument("-t", help = "Path to Kestrel taxonomy file.")
	parser.add_argument("-i", help = "Path to input file of updated taxonomies.")
	parser.add_argument("-o", help = "Path to output csv.")
	u = TaxaUpdater(parser.parse_args())
	u.updateTaxa()
	printRuntime(start)

if __name__ == "__main__":
	main()
