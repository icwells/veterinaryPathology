'''This script will extract summary data for species with at least a given number of records'''

from argparse import ArgumentParser
from datetime import datetime
from records import *
from unixpath import *
from mergeTaxonomy import getTaxa
from vetPathUtils import *
	
class Total():
	# Stores and calculates summary data
	def __init__(self):
		self.total = 0
		self.cancer = 0
		self.male = 0
		self.female = 0
		self.age = 0
		self.agetotal = 0
		self.cancerage = 0
		self.cancertotal = 0
		self.malecancer = 0
		self.femalecancer = 0

	def __str__(self):
		# Calculates rates and returns string
		rate = self.cancer/self.total
		if self.agetotal > 0:
			age = self.age/self.agetotal
		else:
			age = 0.0
		if self.cancertotal > 0:
			cancerage = self.cancerage/self.cancertotal
		else:
			cancerage = 0.0
		return ("{},{},{:.2%},{:.2f},{:.2f},{},{},{},{}").format(self.total, self.cancer, rate, age, cancerage, self.male, self.female, self.malecancer, self.femalecancer)

	def add(self, age, cancer, sex):
		# Update total, cancer rate, age, and sex
		self.total += 1
		sex = sex.lower().strip()
		if sex == "male":
			self.male += 1
		elif sex == "female":
			self.female += 1
		try:
			self.age += float(age)
			self.agetotal += 1
		except ValueError:
			pass
		if cancer == True:
			self.cancer += 1					
			try:
				self.cancerage += float(age)
				self.cancertotal += 1
			except ValueError:
				pass
			if sex == "male":
				self.malecancer += 1
			elif sex == "female":
				self.femalecancer += 1

#-----------------------------------------------------------------------------

class Counter():
	
	def __init__(self, m, infile, outfile, subset):
		self.min = m
		self.infile = infile
		self.outfile = outfile
		self.col = None
		self.d = ""
		self.reps = RepeatIdentifier()
		self.records = {}
		self.taxa = {}
		self.species = []
		self.subset = subset
		self.sub = []

	def __parseHeader__(self, line):
		# Store delimiter and column info
		self.d = getDelim(line)
		self.col = Columns(line.split(self.d))

	def __writeEntries__(self):
		# Writes target species entries to file
		ext = ".txt"
		if self.d == ",":
			ext = ".csv"
		elif self.d == "\t":
			ext = ".tsv"
		outfile = self.outfile[:self.outfile.rfind("/")+1] + ("min{}SpeciesEntries{}").format(self.min, ext)
		print("\tWriting entries file...")
		with open(outfile, "w") as out:
			for line in self.sub:
				out.write(line)	

	def writeRecords(self, taxonomies = None):
		# Writes dict to file
		header = "Kingdom,Phylum,Class,Order,Family,Genus,ScientificName,TotalRecords,CancerRecords,"
		header += "CancerRate,AverageAge(months),AvgAgeCancer(months),Male,Female,maleCancer,femaleCancer\n"
		if self.subset == True:
			self.__writeEntries__()
		print("\tWriting records to file...")
		with open(self.outfile, "w") as out:
			out.write(header)
			for i in self.records.keys():
				row = ("{},{},{}\n").format(",".join(self.taxa[i]), i, self.records[i])
				out.write(row)

	def __updateReplicates__(self):
		# Adds resolved duplicates to totals and makes sure each record still passes the minimum
		rm = []
		for i in self.reps.reps.keys():
			rec = self.reps.reps[i]
			if rec.species in self.records.keys():
				self.records[rec.species].add(rec.age, rec.mass, rec.sex)
		for i in self.records.keys():
			if self.records[i].total < self.min:
				# Delete records which no longer have at least the minimum
				rm.append(i)
		for i in rm:
			del self.records[i]
		print(("\tRemoved {} duplicate records.").format(len(self.records.keys())-len(rm)))

	def __getTaxonomy__(self, row):
		# Stores new taxonomy entries
		self.taxa[row[self.col.Species]] = []
		for i in [self.col.Kingdom, self.col.Phylum, self.col.Class, self.col.Order, self.col.Family, self.col.Genus]:
			self.taxa[row[self.col.Species]].append(row[i])

	def getSpeciesSummaries(self):
		# Returns dict of species totals, cancer rates, # male/female, etc
		first = True
		print("\tGetting records...")
		with open(self.infile, "r") as f:
			for line in f:
				if first == False:
					spl = line.strip().split(self.d)
					if self.col.Max < len(spl):
						n = spl[self.col.Species]
						cancer = False
						if n in self.species:
							if n not in self.records.keys():
								self.records[n] = Total()
							if n not in self.taxa.keys():
								self.__getTaxonomy__(spl)
							age = spl[self.col.Age]
							sex = spl[self.col.Sex]
							if self.col.Code and "8" in spl[self.col.Code]:
								cancer = True
							if self.col.Patient and spl[self.col.Patient] in self.reps.ids:
								# Sort duplicates and store for later
								rec = Record(sex, age, spl[self.col.Patient], n, cancer)
								self.reps.sortReplicates(rec)
							else:
								self.records[n].add(age, cancer, sex)
							if self.subset == True:
								# Keep all target species records
								self.sub.append(line)
				else:
					first = False
					if self.subset == True:
						self.sub.append(line)
		self.__updateReplicates__()

	def setTargetSpecies(self):
		# Gets list of species with at least min entries and identifies duplicates
		totals = {}
		species = []
		first = True
		print("\n\tGetting species totals...")
		with open(self.infile, "r") as f:
			for line in f:
				if first == False:
					spl = line.split(self.d)
					n = spl[self.col.Species]
					# Count number of occurances
					if n not in totals.keys():
						totals[n] = 0
					totals[n] += 1
					# Record names for duplicates
					if self.col.Account and self.col.Patient and self.col.Max < len(spl):
						acc = spl[self.col.Account]
						pat = spl[self.col.Patient]
						self.reps.add(pat, acc)
				else:
					self.__parseHeader__(line)
					first = False
		# Identify replicates and target species
		self.reps.setReplicates()
		for i in totals.keys():
			if totals[i] >= self.min:
				self.species.append(i)

#-----------------------------------------------------------------------------

def checkArgs(args):
	# Check args for errors
	if not args.i or not args.o:
		printError("Please specify input and output files")
	if not os.path.isfile(args.i):
		printError(("Cannot find {}").format(args.i))

def main():
	start = datetime.now()
	parser = ArgumentParser(
"This script will extract summary data for species with at least a given number of records.")
	parser.add_argument("--subset", action = "store_true", default = False,
help = "Print records from target species to additional file.")
	parser.add_argument("-m", type = int, default = 50,
help = "Minimum number of records (default = 100).")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Path to output csv.")
	args = parser.parse_args()
	checkArgs(args)
	counter = Counter(args.m, args.i, args.o, args.subset)
	counter.setTargetSpecies()
	counter.getSpeciesSummaries()
	counter.writeRecords()
	printRuntime(start)

if __name__ == "__main__":
	main()
