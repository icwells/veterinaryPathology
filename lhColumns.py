'''This script defines a class for formatting data from life history files'''

from unixpath import getFileName

class LHcolumns():

	def __init__(self, header, infile):
		# This defines class for storing column numbers and units for life history trait files
		self.Genus = None
		self.Species = None
		self.Fmat = None
		self.Mmat = None
		self.Gest = [None, None]
		self.Wean = [None, None]
		self.Litter = None
		self.LRate = None
		self.ILI = None
		self.Bweight = None
		self.Wweight = None
		self.Aweight = None
		self.Grate = None
		self.Long = [None, None]
		self.MR = None
		self.Max = None
		self.Source = None
		self.__setColumns__(header)
		self.__setSource__(infile)

	def __setUnits__(self, i):
		# Returns units from field
		if "days" in i or "_d" in i:
			return "d"
		elif "(mo)" in i or "_m" in i:
			return "m"
		elif "yrs" in i or "_y" in i:
			return "y"
		elif "Inter-litter/" in i:
			# Assign days to anage interbirth interval
			return "d"
		elif self.Source == "Barton":
			# Return months for Barton gestation
			return "m"

	def __setColumns__(self, header):
		indeces = []
		for idx, i in enumerate(header):
			i = i.strip().lower()
			if "genus" in i:
				self.Genus = idx
				indeces.append(idx)
			elif "species" in i and "sub" not in i:
				# Get first species entry
				self.Species = idx
				indeces.append(idx)
			elif "female maturity" in i.replace("_", " ") or i == "23-1_sexualmaturityage_d":
				self.Fmat = idx
				indeces.append(idx)
			elif "male maturity" in i.replace("_", " "):
				self.Mmat = idx
				indeces.append(idx)
			elif "gestation" in i.lower():
				self.Gest[0] = idx
				self.Gest[1] = self.__setUnits__(i)
				indeces.append(idx)
			elif "weaningweight" in i.replace(" ", "").replace("_", ""):
				self.Wweight = idx
				indeces.append(idx)
			elif "weaning" in i:
				self.Wean[0] = idx
				self.Wean[1] = self.__setUnits__(i)
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
			elif "max" in i and ("longevity" in i or "life" in i):
				self.Long[0] = idx
				self.Long[1] = self.__setUnits__(i)
				indeces.append(idx)
			elif "met" in i and "rate" in i:
				self.MR = idx
				indeces.append(idx)
		if self.Fmat and not self.Mmat:
			# Get assign same maturity age if it is only given for adults
			self.Mmat = self.Fmat
		self.Max = max(indeces)
		self.List = [self.Fmat, self.Mmat, self.Gest, self.Wean, self.Litter, 
self.LRate, self.ILI, self.Bweight, self.Wweight, self.Aweight, self.Grate, self.Long, self.MR]

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
		elif "barton" in name:
			self.Source = "Barton"
		elif "capellini" in name:
			self.Source = "Capellini"
		elif "ernest" in name:
			self.Source = "Ernest"
		if not self.Source:
			print("\n\t[Error] Cannot find source name in filename. Exiting.\n")
			quit()

#-----------------------------------------------------------------------------

	def __literAtmoToW__(self, v):
		# Converts liters of atmosphere/min to watts
		# kylesconverter.com/power/watts-to-litres--atmosphere-per-minute
		v = float(v)
		return str(v*1.68875)

	def __getConvertedUnit__(self, idx, line):
		# Returns converted value if necessary
		if idx[0] and len(line[idx[0]]) > 1 and line[idx[0]] != "-999":
			if idx[1] == "m":
				# Return unformatted value if it is in the output unit
				return line[idx[0]]
			else:
				try:
					# Make sure entry is a number
					n = float(line[idx[0]])
					if idx[1] == "d":
						# Convert days to months (denominator = 365/12)
						return str(n/30.42)
					elif idx[1] == "y":
						# Convert years to months
						return str(n*12)
				except ValueError:
					pass
		return "NA"

	def __getValue__(self, idx, line):
		# Returns value from line
		ret = "NA"
		if idx:
			v = line[idx]
			if len(v) > 1 and v != "-999":
				try:
					# Make sure entry is a number
					n = float(v)
					ret = v
					if idx == self.MR and self.Source == "Amniote":
						# Convert metabolic rate to watts
						ret = self.__literAtmoToW__(v)
				except ValueError:
					pass
		return ret

	def formatLine(self, line, species = None):
		# Returns formatted row for writing
		row = []
		if not species:
			g = line[self.Genus]
			s = line[self.Species]
			species = g.title() + " " + s.lower()
		row.append(species)
		for i in self.List:
			if type(i) == list:
				row.append(self.__getConvertedUnit__(i, line))
			else:
				row.append(self.__getValue__(i, line))
		row.append(self.Source)
		return row

	def updateEntry(self, line, entry, species):
		# Replaces NA values in entry with values from line
		row = []
		row.append(species)
		updated = False
		for idx, i in enumerate(self.List):
			if entry[idx] != "NA":
				# Keep existing value
				val = entry[idx]
			elif type(i) == list:
				val = self.__getConvertedUnit__(i, line)
			else:
				val = self.__getValue__(i, line)
			if val != "NA":
				updated = True
			row.append(val)
		if updated == True:
			# Record both sources
			row.append(entry[-1] + "/" + self.Source)
		else:
			row.append(entry[-1])
		return row, updated
