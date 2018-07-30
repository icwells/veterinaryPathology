'''This script contains common functions for parsing the veterinary pathology database'''

from datetime import datetime

class Columns():

	def __init__(self, header, service = None):
		# Defines a class for identifying and storing column numbers
		self.Service = service
		self.ID = None
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
			if i == "ID":
				self.ID = idx
				indeces.append(idx)
			elif i == "CommonName" or i == "Breed":
				self.Common = idx
				indeces.append(idx)
			elif i == "ScientificName":
				self.Species = idx
				indeces.append(idx)
			elif i == "Age(months)":
				self.Age = idx
				indeces.append(idx)
			elif i == "Days":
				self.Days = idx
				indeces.append(idx)
			elif i == "Sex":
				self.Sex = idx
				indeces.append(idx)
			elif i == "Castrated":
				self.Castrated = None
				indeces.append(idx)
			elif i == "Location":
				self.Location = idx
				indeces.append(idx)
			elif i == "CancerType" or i == "Type":
				self.Type = idx
				indeces.append(idx)
			elif i == "PrimaryTumor" or i == "Primary":
				self.Primary = idx
				indeces.append(idx)
			elif i == "Metastasis":
				self.Metastasis = idx
				indeces.append(idx)
			elif i == "Malignant":
				self.Malignant = idx
				indeces.append(idx)
			elif i == "Necropsy":
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
			elif i == "Client" or i == "Owner":
				self.Submitter = idx
				indeces.append(idx)
			elif i == "Code":
				self.Code = idx
				indeces.append(idx)
		self.Max = max(indeces)

#-----------------------------------------------------------------------------

def getDelim(line):
	# Returns delimiter
	for i in ["\t", ",", " "]:
		if i in line:
			return i
	printError("Cannot determine delimeter. Check file formatting")

def getService(infile):
	# Returns service name from file name
	f = infile.upper()
	for i in ["NWZP", "MSU", "ZEPS"]:
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
