'''Merges NZWP full data file with testgood diagnosis file'''

from datetime import datetime
import unixpath

class Merger():

	def __init__(self):
		self.diagfile = "/home/shawn/Documents/Git/comparativeoncologydata/NWZP/diagnoses/testgood.UTF.tsv"
		self.infile = "/home/shawn/Documents/Git/comparativeoncologydata/NWZP/fulldata.UTF.csv"
		self.outfile = "/home/shawn/Documents/Git/comparativeoncologydata/NWZP/diagnoses/fulldata_withDiagnoses.csv"
		self.diagnoses = {}
		self.head = {}
		self.__setDiagnoses__()

	def __setHeader__(self, row):
		# Stores header as dict of indeces
		for idx, i in enumerate(row):
			self.head[i] = idx

	def __setDiagnoses__(self):
		# Reads in diagnoses as dict
		first = True
		print("\n\tReading diagnosis file...")
		with open(self.diagfile, "r") as f:
			for line in f:
				line = line.strip()
				if first == False:
					row = line.split(d)
					self.diagnoses[row[0]] = row[-1].strip()
				else:
					d = unixpath.getDelim(line)
					self.__setHeader__(line.split(d))
					first = False
		print(("\tExtracted {:,} diagnosis records.").format(len(self.diagnoses)))

	def __checkQuotes__(self, row):
		# Removes extraneous quotes
		ret = []
		for i in row:
			if i.count('"')%2 != 0:
				# Remove odd number of quotes
				i = i.replace('"', '')
			ret.append(i.strip())
		return ret

	def __getDiagnosis__(self, uid, s):
		# Merges comments with diagnosis
		ret = 0
		if uid in self.diagnoses.keys():
			if s and s[-1] != ".":
				s += "."
			s += " " + self.diagnoses[uid]
			ret = 1
		return s, ret

	def mergeDiagnoses(self):
		# Merges full data with diagnoses
		first = True
		count = 0
		print("\tMerging full data file with diagnoses...")
		with open(self.outfile, "w") as out:
			with open(self.infile, "r") as f:
				for line in f:
					line = line.strip()
					if first == False:
						row = line.split(d)
						uid = row[self.head["UID"]].strip()
						if len(row) > self.head["Diagnosis"]:
							row[self.head["Diagnosis"]], c = self.__getDiagnosis__(uid, row[self.head["Diagnosis"]].strip())
							count += c
						row = self.__checkQuotes__(row)
						out.write(",".join(row) + "\n")
					else:
						d = unixpath.getDelim(line)
						self.__setHeader__(line.split(d))
						out.write(line + "\n")
						first = False
		print(("\tMerged {:,} diagnosis records.").format(count))

def main():
	start = datetime.now()
	m = Merger()
	m.mergeDiagnoses()
	print(("\tTotal runtime: {}\n").format(datetime.now() - start))

if __name__ == "__main__":
	main()
