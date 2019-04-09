'''This script contains classes for sorting and storing record data.'''

class Record():
	# Stores record data
	def __init__(self, sex, age, ID, species, mass, sid = None):
		self.sex = sex
		self.age = age
		self.id = ID
		self.species = species
		self.mass = mass
		self.sourceid = sid

class RepeatIdentifier():
	# Class for identifying and resolving repeat entries
	def __init__(self):
		self.entries = {}
		self.ids = []
		self.reps = {}

	def add(self, name, source):
		# Stores number of entry names by source
		if source not in self.entries.keys():
			self.entries[source] = {}
		if name not in self.entries[source].keys():
			self.entries[source][name] = 0
		# Record occurance
		self.entries[source][name] += 1
		
	def setReplicates(self):
		# Stores ids of repeat entries
		for k in self.entries.keys():
			for i in self.entries[k].keys():
				if self.entries[k][i] > 1:
					# Store target id
					self.ids.append(i)
		print(("\tIdentified {:,} duplicate records.").format(len(self.ids)))

	def getSourceIDs(self):
		# Returns list of source IDs from reps
		ret = []
		for k in self.reps.keys():
			if self.reps[k].sourceid is not None:
				ret.append(self.reps[k].sourceid)
		return ret

	def sortReplicates(self, rec):
		# Stores first record or cancer record for each record
		if rec.id not in self.reps.keys():
			self.reps[rec.id] = rec
		elif self.reps[rec.id].mass == False and rec.mass == True:
			# Overwrite with cancer incidence
			self.reps[rec.id] = rec
