'''Identifies species which have significant discrepancies between number of necropsies and non-necropsies'''

from argparse import ArgumentParser
from datetime import datetime
from math import sqrt
import operator
import unixpath

CASES = "No.Cases"
DEATHBOOKS = "Adults only"
NAME = "Common_Name"
SPECIES = "Taxa"
ZIMS = "No.Deaths Oct 2000-Oct2020 ZIMS"

class Species():

	def __init__(self, species, common, cases, zims, db):
		self.common = common
		self.species = species
		self.keep = True
		for i in [zims, db]:
			if not i.strip() or i == "N/A":
				self.keep = False
		if self.keep:
			try:
				self.cases = int(cases)
				self.deathbooks = int(db)
				self.dbprev = self.cases/self.deathbooks
				self.difference = 0
				self.significant = 0
				self.variance = None
				self.zims = int(zims)
				self.zprev = self.cases/self.zims
				self.__setSignificance__()
			except:
				self.keep = False

	def toList(self):
		# Returns list of record values
		return [self.species, self.common, str(self.zims), str(self.deathbooks), str(self.variance), str(self.difference), str(self.significant)]

	def __setSignificance__(self):
		# Stores absolute value of difference between number of records
		self.difference = abs(self.deathbooks - self.zims)
		if self.deathbooks < self.zims:
			n = self.deathbooks
			p = self.dbprev
		else:
			n = self.zims
			p = self.zprev
		self.variance = 2 * sqrt(n * p * (1 - p)) / n
		if self.difference > self.variance:
			self.significant = 1

class NecropsyVariance():

	def __init__(self, args):
		self.min = 50
		self.outfile = args.o
		self.records = {}
		self.rows = []
		self.__setCounts__(args.i)
		self.__filter__()
		self.__write__()

	def __setCounts__(self, infile):
		# Gets species counts
		first = True
		print("\n\tReading {}...".format(infile))
		for i in unixpath.readFile(infile, header = True, d = ","):
			if not first:
				sp = i[header[SPECIES]]
				self.records[sp] = Species(sp, i[header[NAME]], i[header[CASES]], i[header[ZIMS]], i[header[DEATHBOOKS]])
			else:
				header = i
				first = False

	def __filter__(self):
		# Removes species which are missing a records class and sorts remaining records
		for k in self.records.keys():
			r = self.records[k]
			if r.keep:
				self.rows.append(self.records[k])
		self.rows.sort(key=operator.attrgetter("difference"), reverse=True)
		self.rows.sort(key=operator.attrgetter("significant"), reverse=True)

	def __write__(self):
		# Writes records to file
		print("\tWriting records to file...")
		with open(self.outfile, "w") as out:
			out.write("Species,CommonNames,ZIMSNecropsies,DeathbooksNecropsies,SignificantDifference,Difference,Significant\n")
			for i in self.rows:
				out.write(",".join(i.toList()) + "\n")

def main():
	start = datetime.now()
	parser = ArgumentParser("Identifies species which have significant discrepancies between number of necropsies and non-necropsies.")
	parser.add_argument("-i", help = "Path to neoplasia prevalence file for non-necropsy records.")
	parser.add_argument("-o", help = "Path to output file.")
	NecropsyVariance(parser.parse_args())
	print(("\tTotal runtime: {}\n").format(datetime.now() - start))

if __name__ == "__main__":
	main()
