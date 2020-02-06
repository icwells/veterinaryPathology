'''Extracts account info from file if id is in given file'''

from argparse import ArgumentParser
from datetime import datetime
import os
import unixpath

class Filter():
	def __init__(self, args):
		self.ids = set()
		self.infile = args.a
		self.outfile = args.o
		self.__setIDs__(args.i)

	def __setIDs__(self, infile):
		# Reads ids file
		with open(infile, "r") as f:
			for line in f:
				self.ids.add(line.strip())

	def filter(self):
		# Writes accounts with id in ids to outfile
		first = True
		with open(self.outfile, "w") as out:
			with open(self.infile, "r") as f:
				for line in f:
					if not first:
						i = line.split(d)[0]
						if i in self.ids:
							out.write(line)
					else:
						d = unixpath.getDelim(line)
						out.write(line)
						first = False

def main():
	start = datetime.now()
	parser = ArgumentParser("Extracts account info from file if id is in given file")
	parser.add_argument("-i", help = "Path to target IDs file (one column).")
	parser.add_argument("-a", help = "Path to accounts file.")
	parser.add_argument("-o", help = "Path to output file.")
	f = Filter(parser.parse_args())
	f.filter()
	print(("\tTotal runtime: {}\n").format(datetime.now() - start))

if __name__ == "__main__":
	main()
