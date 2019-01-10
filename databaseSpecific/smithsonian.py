'''This script will merge Smithsonian National Zoo data, remove dupliates, and calcultate species totals'''

import os
from argparse import ArgumentParser
from datetime import datetime
from glob import glob
import unixpath
from smithUtils import *

class SmithsonianParser():

	def __init__(self, indir, outfile):
		self.columns = None
		self.records = {}
		self.species = {}
		self.indir = unixpath.checkDir(indir)
		self.outfile = outfile
		self.ext = unixpath.getExt(self.outfile)
		self.delim = self.__setDelim__()
		self.totalsfile = self.__setTotalsFile__()
		self.header = "Accession,CommonName,Species,Pathology#,DateOfDeath,MannerOfDeath,\
CauseOfDeath,Tumor,Location,Type,CancerDiagnosis,Malignant,MorphologicalDiagnosis\n"
		# Make sure input directory exists
		unixpath.checkDir(self.indir)

	def __setDelim__(self):
		# Stores delimiter for output files
		d = ","
		if self.ext == "tsv" or self.ext == ".txt":
			d = "\t"
		return d
		
	def __setTotalsFile__(self):
		# Stores name of species total file and makes sure output directory exists
		path = os.path.split(self.outfile)[0]
		path = unixpath.checkDir(path, True)
		return os.path.join(path, "smithsonianSpeciesTotals." + self.ext)

	def writeRecords(self):
		# Writes record dict to file
		print("\tWriting records to file...")
		with open(self.outfile, "w") as out:
			out.write(self.header)
			for i in self.records.keys():
				out.write("{}\n".format(self.records[i]))

	def __writeTotals__(self):
		# Writes species totals to file
		print("\tWriting species totals to file...")
		with open(self.totalsfile, "w") as out:
			out.write("Species,CommonName,Number\n")
			for i in self.species.keys():
				if self.species[i].new > 0:
					out.write("{}\n".format(self.species[i]))

	def getSpeciesTotals(self):
		# Recounts total entries, updates species names in records, and writes totals to file
		print("\tCalculating species totals...")
		for i in self.records.keys():
			n = self.records[i].name
			if n in self.species.keys():
				# Store species name and add 1 total
				self.records[i].species = self.species[n].species
				self.species[n].new += 1
		self.__writeTotals__()

	def __readInfile__(self, infile, diagnosis, malignant):
		# Sorts and stores records from input file
		first = True
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					s = line.strip().split(d)
					if len(s) == self.columns.length:
						if s[0] in self.records.keys():
							self.records[s[0]].resolveRecord(self.columns, s)
						else:
							self.records[s[0]] = Record(malignant, self.delim, diagnosis)
							self.records[s[0]].setRecord(self.columns, s)
				else:
					d = unixpath.getDelim(line)
					if self.columns is None:
						self.columns = Columns(line.split(d))
					first = False

	def parseInputDirectory(self):
		# Reads files from indir
		print("\tReading input files...")
		for i in glob(self.indir + "*"):
			malignant = False
			diagnosis = unixpath.getFileName(i)
			if diagnosis == "malignant":
				malignant = True
			elif "_" in diagnosis:
				diagnosis = "NA"
			self.__readInfile__(i, diagnosis, malignant)


	def __getRow__(self, d, line):
		# Returns row with emtpy cells removed
		ret = []
		s = line.strip().split(d)
		for i in s:
			if i.strip():
				ret.append(i)
		return ret

	def setSpecies(self, indir):
		# Calls stores species as dict of classes
		print("\n\tReading species totals files...")
		for i in glob(indir + "*"):
			first = True
			with open(i, "r") as f:
				for line in f:
					if first == True:
						d = unixpath.getDelim(line)
						first = False
					s = self.__getRow__(d, line)
					if len(s) >= 3:
						if s[-1] in self.species.keys():
							self.species[s[-1]].resolveSpecies(s)
						else:
							self.species[s[-1]] = Species(self.delim, s)

def main():
	start = datetime.now()
	parser = ArgumentParser("This script will merge Smithsonian National Zoo data, remove dupliates, and calcultate species totals.")
	parser.add_argument("-i", required = True, help = "Path to input directory")
	parser.add_argument("-t", required = True, help = "Path to species total directory.")
	parser.add_argument("-o", required = True, help = "Path to output file (species total file will be written to same directory).")
	args = parser.parse_args()
	p = SmithsonianParser(args.i, args.o)
	p.setSpecies(unixpath.checkDir(args.t))
	p.parseInputDirectory()
	p.getSpeciesTotals()
	p.writeRecords()
	print(("\tFinished. Run time: {}\n").format(datetime.now()-start))

if __name__ == "__main__":
	main()
