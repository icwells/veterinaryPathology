'''Records species totals from London Zoo deathbooks and population files'''

from argparse import ArgumentParser
from datetime import datetime
from glob import glob
import os
import pandas
import unixpath

class SpeciesTotals():

	def __init__(self, args):
		unixpath.checkFile(args.d)
		self.indir = unixpath.checkDir(args.p)
		self.infile = args.d
		self.outfile = args.o
		self.species = {}
		self.__readDeathBooks__()
		self.__readPopulationFiles__()
		self.__write__()

	def __addSpecies__(self, sp, count=None):
		# Adds species to totals dict
		if sp not in self.species.keys():
			self.species[sp] = [0, 0]
		if count:
			self.species[sp][1] += count
		else:
			self.species[sp][0] += 1

	def __readDeathBooks__(self):
		# Records totals LZ deathbooks
		first = True
		print("\n\tReading species from deathbooks...")
		for line in unixpath.readFile(self.infile):
			if not first:
				self.__addSpecies__(line[h["Scientific name"]])
			else:
				h = line
				first = False

	def __readPopulationFiles__(self):
		# Iterates over population directory
		print("\tReading species from population files...")
		for i in glob(os.path.join(self.indir, "*/*.xls")):
			df = pandas.read_excel(i)
			for line in df.iterrows():
				count = 0
				for i in ["DeathsMale", "DeathsFemale", "DeathsOther"]:
					try:
						count += int(line[i])
					except:
						pass
				if count > 0:
					self.__addSpecies__(line["PreferredScientificName"], count)

	def __write__(self):
		# Writes dict to file
		print("\tWriting species counts to file..")
		with open(self.outfile, "w") as out:
			out.write("Species,DeathBooks,PopulationRecords\n")
			for k in self.species.keys():
				out.write("{},{},{}\n".format(k, self.species[k][0], self.species[k][1]))

def main():
	start = datetime.now()
	parser = ArgumentParser("Records species totals from London Zoo deathbooks and population files.")
	parser.add_argument("-d", help = "Path to deathbooks file.")
	parser.add_argument("-p", help = "Path to directory of popultion data.")
	parser.add_argument("-o", help = "Path to output file.")
	SpeciesTotals(parser.parse_args())
	print(("\tTotal runtime: {}\n").format(datetime.now() - start))

if __name__ == "__main__":
	main()
