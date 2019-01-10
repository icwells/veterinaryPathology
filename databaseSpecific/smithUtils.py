'''Helper classes and functions for smithsonian.py'''

from glob import glob

class Record():

	def __init__(self, malignant, delim, diag = None):
		self.__delim__ = delim
		self.id = None
		self.name = None
		self.species = None
		self.num = None
		self.date = None
		self.manner = None
		self.cause = None
		self.tumor = False
		self.location = None
		self.type = None
		self.diagnosis = diag
		self.malignant = malignant
		self.comments = None

	def __str__(self):
		# Converts to string for writing output
		ret = []
		for i in [self.id, self.name, self.species, self.num, self.date, 
						self.manner, self.cause, self.tumor, self.location, self.type, 
						self.diagnosis, self.malignant, self.comments]:
			if i is None:
				ret.append("NA")
			elif type(i) == bool:
				if i == False:
					ret.append("N")
				else:
					ret.append("Y")
			elif not i.strip():
				ret.append("NA")
			else:
				ret.append(i)
		return self.__delim__.join(ret)

	def __setTumor__(self, cause):
		# Sets tumor value
		if self.tumor == False:
			if "tumor" in cause.lower():
				self.tumor = True
			elif self.diagnosis is not None and self.diagnosis != "NA":
				self.tumor = True

	def setRecord(self, col, row):
		# Parses row to store record data
		idx = 0
		self.id = row[col.id]
		self.name = row[col.name]
		self.num = row[col.num]
		self.date = row[col.date]
		self.manner = row[col.manner]
		self.cause = row[col.cause]
		self.__setTumor__(row[col.cause])
		d = row[col.cause].split(";")
		if self.tumor == True:
			idx = 1
		if len(d) > idx:
			self.location = d[idx]
			self.type = ";".join(d[idx+1:])
		self.comments = row[col.diag]

	def __resolveStrings__(self, target, value):
		# Resolves individual attributes
		if target is None or not target.strip() or target == "NA":
			if value.strip():
				return value
		return target

	def __addStrings__(self, target, value):
		# Adds new info to attribute
		if target is None or not target.strip():
			return value
		elif value not in target:
			return target + "::" + value
		return target

	def resolveRecord(self, col, row):
		# Adds info from additional rows
		idx = 0
		self.name = self.__resolveStrings__(self.name, row[col.name])
		self.num = self.__resolveStrings__(self.num, row[col.num])
		self.date = self.__resolveStrings__(self.date, row[col.date])
		self.manner = self.__resolveStrings__(self.manner, row[col.manner])
		self.cause = self.__resolveStrings__(self.cause, row[col.cause])
		self.__setTumor__(row[col.cause])
		if row[col.cause].strip():
			d = row[col.cause].split(";")
			if "tumor" in d[0].lower():
				idx = 1
			if len(d) > idx:
				self.location = self.__addStrings__(self.location, d[idx])
				self.type = self.__addStrings__(self.type, ";".join(d[idx+1:]))
			self.comments = self.__addStrings__(self.comments, row[col.diag])

#-----------------------------------------------------------------------------

class Species():

	def __init__(self, delim, row):
		self.__delim__ = delim
		self.species = None
		self.common = None
		self.old = 0
		self.new = 0
		self.__setFromRow__(row)

	def __str__(self):
		# Formats string output
		return self.__delim__.join([self.species, self.common, str(self.new)])

	def __binomial__(self, name):
		# Returns formatted binomial species name
		ret = []
		s = name.lower().split()
		for idx, i in enumerate(s):
			if idx == 0:
				ret.append(i.title())
			elif "(" not in i and ")" not in i:
				ret.append(i)
		return " ".join(ret)

	def __setFromRow__(self, row):
		# Stores data from row
		self.common = row[2]
		self.species = self.__binomial__(row[1])
		self.old = int(float(row[0]))

	def resolveSpecies(self, row):
		# Determines which scientific name to store in case of duplicates
		n = int(float(row[0]))
		if n > self.old:
			self.species = self.__binomial__(row[1])
			self.old = n

#-----------------------------------------------------------------------------

class Columns():

	def __init__(self, header):
		self.id = None
		self.name = None
		self.num = None
		self.date = None
		self.manner = None
		self.cause = None
		self.diag = None
		self.length = len(header)
		self.__parseHeader__(header)

	def __parseHeader__(self, header):
		# Stores column indeces
		for idx, i in enumerate(header):
			i = i.strip()
			if i == "Accession No.":
				self.id = idx
			elif i == "Common Name":
				self.name = idx
			elif i == "Pathology No":
				self.num = idx
			elif i == "Date of Death":
				self.date = idx
			elif i == "Manner of Death":
				self.manner = idx
			elif i == "Cause of Death":
				self.cause = idx
			elif i == "Morphologic Diagnosis":
				self.diag = idx
