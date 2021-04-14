'''Inserts species and genus into london zoo records.'''

from argparse import ArgumentParser
from datetime import datetime
import os
import unixpath

class Species():

	def __init__(self, args):
		self.d = ","
		self.infile = args.i
		self.outfile = args.o
		self.taxa = {}
		self.__setTaxa__(args.p)
		self.__insertSpecies__()

	def __setTaxa__(self, infile):
		# Stores species and genus by common name
		first = True
		print("\n\tReading preformatted file...")
		for i in unixpath.readFile(infile, d = self.d):
			if not first:
				c = i[h["CommonName"]]
				if c not in self.taxa.keys():
					s = i[h["ScientificName"]]
					if " " not in s:
						# Store genus only
						self.taxa[c] = [s]
					else:
						self.taxa[c] = [s.split()[0], s]				
			else:
				h = i
				first = False

	def __insertSpecies__(self):
		# Added species and genus to input file
		first = True
		print("\tReading input file...")
		with open(self.outfile, "w") as out:
			for i in unixpath.readFile(self.infile, d = self.d):
				if not first:
					c = i[h["Name"]]
					if c in self.taxa.keys():
						i[h["Genus"]] = self.taxa[c][0]
						if len(self.taxa[c]) > 1:
							i[h["Species"]] = self.taxa[c][1]
					out.write(self.d.join(i) + "\n")
				else:
					h = i
					head = [-1] * len(h)
					for k in i.keys():
						head[h[k]] = k
					out.write(self.d.join(head) + "\n")
					first = False

def main():
	start = datetime.now()
	parser = ArgumentParser("Inserts species and genus into london zoo records.")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Path to output file.")
	parser.add_argument("-p", help = "Path to preformatted file.")
	Species(parser.parse_args())
	print(("\tTotal runtime: {}\n").format(datetime.now() - start))

if __name__ == "__main__":
	main()
