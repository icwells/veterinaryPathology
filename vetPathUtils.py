'''This script contains common functions for parsing the veterinary pathology database'''

from datetime import datetime
from unixpath import getFileName

class Columns():

	def __init__(self, header, service = None):
		# Defines a class for identifying and storing column numbers
		self.Service = service
		self.ID = None
		self.Genus = None
		self.Species = None
		self.Common = None
		self.Age = None
		self.Days = None
		self.Sex = None
		self.Castrated = None
		self.Location = None
		self.Type = None
		self.Primary = None
		self.Metastasis = None
		self.Malignant = None
		self.Necropsy = None
		self.Date = None
		self.Comments = None
		self.Account = None
		self.Submitter = None
		self.Account = None
		self.Code = None
		self.__setColumns__(header)

	def __setColumns__(self, header):
		# Assigns column numbers from header
		indeces = []
		for idx, i in enumerate(header):
			i = i.strip()
			if i == "ID" or i == "Origin ID":
				self.ID = idx
				indeces.append(idx)
			elif i.replace(" ", "") == "CommonName" or i == "Breed":
				self.Common = idx
				indeces.append(idx)
			elif i == "ScientificName" or i == "Binomial Scientific":
				self.Species = idx
				indeces.append(idx)
			elif i == "Age(months)" or i == "Age":
				self.Age = idx
				indeces.append(idx)
			elif i == "Days":
				self.Days = idx
				indeces.append(idx)
			elif i == "Sex":
				self.Sex = idx
				indeces.append(idx)
			elif i == "Castrated":
				self.Castrated = idx
				indeces.append(idx)
			elif i == "Location" or i == "Tissue":
				self.Location = idx
				indeces.append(idx)
			elif i.replace(" ", "") == "CancerType" or i == "Type":
				self.Type = idx
				indeces.append(idx)
			elif i == "PrimaryTumor" or i == "Primary":
				self.Primary = idx
				indeces.append(idx)
			elif i == "Metastasis" or i == "Metastatic":
				self.Metastasis = idx
				indeces.append(idx)
			elif i == "Malignant":
				self.Malignant = idx
				indeces.append(idx)
			elif i == "Necropsy" or i == "Death via Cancer Y/N":
				self.Necropsy = idx
				indeces.append(idx)
			elif "Date" in i:
				self.Date = idx
				indeces.append(idx)
			elif i == "Diagnosis" or i == "Comments":
				self.Comments = idx
				indeces.append(idx)
			elif i == "Account":
				self.Account = idx
				indeces.append(idx)
			elif i == "Client" or i == "Owner" or i == "Institution ID":
				self.Submitter = idx
				indeces.append(idx)
			elif i == "Code" or i.replace(" ", "") == "CancerY/N":
				self.Code = idx
				indeces.append(idx)
		self.Max = max(indeces)

#-----------------------------------------------------------------------------

class LHcolumns():

	def __init__(self, header, infile):
		# This defines class for storing column numbers for life history trait files
		self.Species = None
		self.Fmat = None
		self.Mmat = None
		self.Gest = None
		self.Wean = None
		self.Litter = None
		self.LRate = None
		self.ILI = None
		self.Bweight = None
		self.Wweight = None
		self.Aweight = None
		self.Grate = None
		self.Long = None
		self.MR = None
		self.Max = None
		self.Source = None
		self.__setColumns__(header)
		self.__setSource__(infile)

	def __setColumns__(self, header):
		indeces = []
		for idx, i in enumerate(header):
			i = i.strip().lower()
			if "genus" in i:
				self.Genus = idx
				indeces.append(idx)
			elif "species" in i and "sub" not in i:
				self.Species = idx
				indeces.append(idx)
			elif "female maturity" in i.replace("_", " ") or i == "23-1_sexualmaturityage_d":
				self.Fmat = idx
				indeces.append(idx)
			elif "male maturity" in i.replace("_", " "):
				self.Mmat = idx
				indeces.append(idx)
			elif "gestation" in i.lower():
				self.Gest = idx
				indeces.append(idx)
			elif "weaningweight" in i.replace(" ", "").replace("_", ""):
				self.Wweight = idx
				indeces.append(idx)
			elif "weaning" in i:
				self.Wean = idx
				indeces.append(idx)
			elif "litter" in i and "size" in i:
				self.Litter = idx
				indeces.append(idx)
			elif "litters" in i and ("year" in i or "per_y" in i):
				self.LRate = idx
				indeces.append(idx)
			elif "interbirth" in i:
				self.ILI = idx
				indeces.append(idx)
			elif ("birth" in i and "weight" in i) or i == "5-3_neonatebodymass_g":
				self.Bweight = idx
				indeces.append(idx)
			elif "adult" in i and ("weight" in i or "mass" in i):
				self.Aweight = idx
				indeces.append(idx)
			elif "growth rate" in i:
				self.Grate = idx
				indeces.append(idx)
			elif "max" in i and "longevity" in i:
				self.Long = idx
				indeces.append(idx)
			elif "met" in i and "rate" in i:
				self.MR = idx
				indeces.append(idx)
		if self.Fmat and not self.Mmat:
			# Get assign same maturity age if it is only given for adults
			self.Mmat = self.Fmat
		self.Max = max(indeces)
		self.List = [self.Fmat, self.Mmat, self.Gest, self.Wean, self.Litter, 
self.LRate, self.ILI, self.Bweight, self.Wweight, self.Aweight, self.Grate, self.Long]

	def __setSource__(self, infile):
		# Sets source name from input file name
		name = getFileName(infile)
		name = name.lower()
		if "anage" in name:
			self.Source = "anAge"
		elif "pantheria" in name:
			self.Source = "panTHERIA"
		elif "amniote" in name:
			self.Source = "Amniote"
		if not self.Source:
			print("\n\t[Error] Cannot find source name in filename. Exiting.\n")
			quit()

	def formatLine(self, line, species = None):
		# Returns formatted row for writing
		row = []
		if not species:
			g = line[self.Genus]
			s = line[self.Species]
			species = g.title() + " " + s.lower()
		row.append(species)
		for i in self.List:
			if i and len(line[i]) > 1 and line[i] != "-999":
				try:
					# Make sure entry is a number
					n = float(line[i])
					row.append(line[i])
				except ValueError:
					row.append("NA")
			else:
				row.append("NA")
		if self.MR and len(line[self.MR]) > 1 and line[self.MR] != "-999":
			# Convert metabolic rate to watts if needed
			if self.Source == "Amniote":
				row.append(literAtmoToW(line[self.MR]))
			else:
				row.append(line[self.MR])
		else:
			row.append("NA")
		row.append(self.Source)
		return row

	def updateEntry(self, line, entry, species):
		# Replaces NA values in entry with values from line
		row = []
		row.append(species)
		updated = False
		for idx, i in enumerate(self.List):
			if entry[idx] != "NA":
				row.append(entry[idx])
			elif i and len(line[i]) > 1 and line[i] != "-999":
				try:
					# Make sure entry is a number
					n = float(line[i])
					row.append(line[i])
					updated = True
				except ValueError:
					row.append("NA")
			else:
				row.append("NA")
		if entry[-2] != "NA":
			row.append(entry[-2])
		elif self.MR and len(line[self.MR]) > 1 and line[self.MR] != "-999":
			# Convert metabolic rate to watts if needed
			if self.Source == "Amniote":
				row.append(literAtmoToW(line[self.MR]))
			else:
				row.append(line[self.MR])
		else:
			row.append("NA")
		if updated == True:
			# Record both sources
			row.append(entry[-1] + "/" + self.Source)
		else:
			row.append(entry[-1])
		return row, updated

#-----------------------------------------------------------------------------

def literAtmoToW(v):
	# Converts liters of atmosphere/min to watts
	v = float(v)
	return str(v*1.68875)

def getDelim(line):
	# Returns delimiter
	for i in ["\t", ",", " "]:
		if i in line:
			return i
	printError("Cannot determine delimeter. Check file formatting")

def getService(infile):
	# Returns service name from file name
	f = infile.upper()
	for i in ["DLC", "NWZP", "MSU", "ZEPS"]:
		if i in f:
			return i
	if "testgood" in infile:
		return "NWZP"
	printError("Cannot find service name in file name")

def printError(msg):
	# Prints formatted error message and quits
	print(("\n\t[Error] {}. Exiting.\n").format(msg))
	quit()

def printRuntime(start):
	# Prints elsapsed time
	print(("\tFinished. Runtime: {}\n").format(datetime.now() - start))
