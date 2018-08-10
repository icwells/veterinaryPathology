'''This script defines a class for formatting data from life history files'''

class LHcolumns():

	def __init__(self, header, infile):
		# This defines class for storing column numbers and units for life history trait files
		self.Species = None
		self.Fmat = None
		self.Mmat = None
		self.Gest = [None, None, "d"]
		self.Wean = [None, None, "d"]
		self.Litter = None
		self.LRate = None
		self.ILI = None
		self.Bweight = None
		self.Wweight = None
		self.Aweight = None
		self.Grate = None
		self.Long = [None, None, "m"]
		self.MR = None
		self.Max = None
		self.Source = None
		self.__setColumns__(header)
		self.__setSource__(infile)

	def __setUnits__(i):
		# Returns units from field
		if "days" in i or "_d" in i:
			return "d"
		elif "(mo)" in i or "_m" in i:
			return "m"
		elif "yrs" in i or "_y" in i:
			return "y"		

	def __setColumns__(self, header):
		indeces = []
		for idx, i in enumerate(header):
			i = i.strip().lower()
			if "genus" in i:
				self.Genus = idx
				indeces.append(idx)
			elif "species" in i and not self.Species:
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
		elif "barton" in name:
			self.Source = "Barton"
		elif "capellini" in name:
			self.Source = "Capellini"
		elif "ernest" in name:
			self.Source = "Ernest"
		if not self.Source:
			print("\n\t[Error] Cannot find source name in filename. Exiting.\n")
			quit()

	def __getConvertedUnit__(self, key, line):
		# Returns converted value if necessary
		

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

