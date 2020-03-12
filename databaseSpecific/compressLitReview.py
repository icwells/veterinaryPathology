'''Merges data from Madsen book with parsed diagnoses and taxonomies'''

from argparse import ArgumentParser
from datetime import datetime
import os
import unixpath

class Tumor():
	def __init__(self, ty, loc, mal, cls = None):
		self.type = ty
		self.location = ""
		self.malignant = ""
		self.classification = cls
		if loc:
			self.location = loc
		if mal:
			self.malignant = mal

	def toList(self):
		# Returns values as list
		ret = [self.type, self.location, self.malignant]
		if self.classification:
			ret.append(self.classification)
		return ret		

class Record():
	def __init__(self, species, common):
		self.taxonomy = ["NA", "NA", "NA", "NA", "NA","NA"]
		self.species = species
		self.common = common
		self.orig = {}
		self.diagnoses = {}

	def add(self, ty, loc, mal, cls = None):
		# Adds novel tumor types to dict
		if cls:
			if ty not in self.orig.keys():
				self.orig[ty] = Tumor(ty, loc, mal, cls)
		else:
			if ty not in self.diagnoses.keys():
				self.diagnoses[ty] = Tumor(ty, loc, mal)

	def __formatRecord__(self, d):
		# Formats records from dict
		t = []
		l = []
		m = []
		c = []
		for k in d.keys():
			t.append(d[k].type)
			l.append(d[k].location)
			m.append(d[k].malignant)
			'''if d[k].classification:
				t.append(d[k].classification)'''
		ret = [";".join(t), ";".join(l), ";".join(m)]
		if len(c) > 0:
			ret.append(";".join(c))
		return ret

	def toString(self):
		# Formats data for writing to file
		ret = self.taxonomy
		ret.append(self.species)
		ret.append(self.common)
		ret.extend(self.__formatRecord__(self.orig))
		ret.extend(self.__formatRecord__(self.diagnoses))
		return (",".join(ret).replace(",;", ",") + "\n")

class Compress():

	def __init__(self, args):
		for i in [args.i, args.t]:
			unixpath.checkFile(i)
		self.infile = args.i
		self.outfile = os.path.join(os.path.split(self.infile)[0], "compressed_literature_compilation.csv")
		self.header = {}
		self.records = {}
		self.taxa = {}
		self.names = []
		self.__setTaxa__(args.t)
		self.__readFile__()
		self.__writeRecords__()

	def __writeRecords__(self):
		# Writes compressed records to outfile
		print("\tWriting results to file...")
		with open(self.outfile, "w") as out:
			head = self.names
			head.append("CommonName")
			for i in range(2):
				head.append("TumorType,Location,Malignant")
				'''if i == 0:
					head.append("Classification")'''
			out.write(",".join(head) + "\n")
			for k in self.records.keys():
				out.write(self.records[k].toString())

	def __parseLine__(self, row):
		# Extracts dat from single line
		try:
			sp = row[self.header["Scientific Name"]]
			if sp not in self.records.keys():
				# Initialize unique species record
				self.records[sp] = Record(sp, row[self.header["Common Name"]])
				if sp in self.taxa.keys():
					self.records[sp].taxonomy = self.taxa[sp]
			# Summarize columns from lit review
			for i in range(1, 4):
				t = row[self.header["Tumor{}_diagnosis".format(i)]].strip()
				m = row[self.header["Benign_Malignant_Tumor{}".format(i)]].strip()
				c = row[self.header["General_classification_tumor{}".format(i)]].strip()
				l = row[self.header["tumor_location{}".format(i)]].strip()
				self.records[sp].add(t, l, m, c)
			# Get values from parseRecords
			t = row[self.header["TumorType"]].strip().split(";")
			l = row[self.header["Location"]].strip().split(";")
			m = row[self.header["Malignant"]].strip()
			for idx, i in enumerate(t):
				self.records[sp].add(i, l[idx], m)
		except IndexError:
			pass

	def __readFile__(self):
		# Reads file and compresses data
		first = True
		ret = {}
		d = ","
		print(("\tReading {}...").format(os.path.split(self.infile)[1]))
		with open(self.infile, "r") as f:
			for line in f:
				line = line.strip()
				if not first:
					self.__parseLine__(line.split(d))
				else:
					for idx, i in enumerate(line.split(d)):
						self.header[i] = idx
					first = False

	def __setTaxa__(self, infile):
		# Stores references and species names
		first = True
		print("\n\tReading taxonomy...")
		with open(infile, "r") as f:
			for line in f:
				line = line.strip()
				if not first:
					s = line.split(d)
					self.taxa[s[-2]] = s[1:-2]
				else:
					d = unixpath.getDelim(line)
					self.names = line.split(d)[1:-1]
					first = False

def main():
	start = datetime.now()
	parser = ArgumentParser("Merges data from Madsen book with parsed diagnoses and taxonomies")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-t", help = "Path to taxonomy file.")
	print()
	Compress(parser.parse_args())
	print(("\tTotal runtime: {}\n").format(datetime.now() - start))

if __name__ == "__main__":
	main()
