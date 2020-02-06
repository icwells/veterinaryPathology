'''Merges data from Madsen book with parsed diagnoses and taxonomies'''

from argparse import ArgumentParser
from datetime import datetime
import os
import unixpath

class Merger():

	def __init__(self, args):
		for i in [args.i, args.t, args.d]:
			unixpath.checkFile(i)
		self.infile = args.d
		self.outfile = os.path.join(os.path.split(self.infile)[0], "madsenMergedDiagnoses.csv")
		self.refs = {}
		self.taxa = {}
		self.__setRefs__(args.i)
		self.__setTaxa__(args.t)

	def __readFile__(self, infile):
		# Reads file and returns dict
		first = True
		ret = {}
		print(("\tReading {}...").format(os.path.split(infile)[1]))
		with open(infile, "r") as f:
			for line in f:
				line = line.strip()
				if not first:
					s = line.split(d)
					# Store with ID as key
					ret[s[0]] = s[1:]
				else:
					d = unixpath.getDelim(line)
					h = line.split(d)
					first = False
		return ret, h

	def __setRefs__(self, infile):
		# Stores references and species names
		data, _ = self.__readFile__(infile)
		for k in data.keys():
			self.refs[k] = [data[k][0], data[k][-1]]

	def __setTaxa__(self, infile):
		# Stores references and species names
		data, _ = self.__readFile__(infile)
		for k in data.keys():
			# Store kingdom-genus
			self.taxa[data[k][6]] = data[k][:6]

	def merge(self):
		# Merges diagnosis file with other input
		head = []
		data, h = self.__readFile__(self.infile)
		with open(self.outfile, "w") as out:
			out.write("ID,Kingdom,Phylum,Class,Orders,Family,Genus,Species,{},Reference\n".format(",".join(h[1:])))
			for k in data.keys():
				row = [k]
				t = ["NA", "NA", "NA", "NA", "NA", "NA"]
				sp, r = "NA", "NA"
				if k in self.refs.keys():
					sp, r = self.refs[k]
				if sp in self.taxa.keys():
					t = self.taxa[sp]
				row.extend(t)
				row.append(sp)
				row.extend(data[k])
				row.append(r)
				out.write(",".join(row) + "\n")

def main():
	start = datetime.now()
	parser = ArgumentParser("Merges data from Madsen book with parsed diagnoses and taxonomies")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-t", help = "Path to taxonomy file.")
	parser.add_argument("-d", help = "Path to parsed diagnoses.")
	print()
	m = Merger(parser.parse_args())
	m.merge()
	print(("\tTotal runtime: {}\n").format(datetime.now() - start))

if __name__ == "__main__":
	main()
