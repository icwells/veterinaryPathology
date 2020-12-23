'''Preformats London Zoo data before parsing by compOncDB.'''

from argparse import ArgumentParser
from datetime import datetime
from os.path import split, join
import re
from string import punctuation
from unixpath import readFile

class LondonZoo():

	def __init__(self, args):
		digits = "([0-9]+[.]?([0-9]+))"
		self.count = 0
		self.digits = re.compile(digits)
		self.days = re.compile("{}\s?(d|day)".format(digits))
		self.header = None
		self.infile = args.i
		self.months = re.compile("{}\s?(m|mnths|month)".format(digits))
		self.outfile = join(split(self.infile)[0], "LondonZoo.Preformatted.csv")
		self.outheader = "CommonName,ScientificName,AgeCategory,Age,Sex,Date,Year,Comments,Account\n"
		self.total = 0
		self.years = re.compile("{}\s?(y|year)".format(digits))

	def __removePunctuation__(self, val):
		# Removes leading punctuation marks
		if val and val[0] in punctuation:
			val = val[1:]
		return val

	def __setAccount__(self, line):
		# Stores account numbers
		ret = line[2].strip()
		acc = line[self.header["Code"]].strip()
		if "/" not in acc and "-" not in acc:
			ret = "{}-{}".format(ret, acc)
		return ret

	def __setWeight__(self, line):
		# Converts kg to grams
		ret = ""
		g = self.digits.search(line[self.header["Wt - g"]])
		if g:
			ret = g.group(0)
		else:
			kg = self.digits.search(line[self.header["Wt - kg"]])
			if kg:
				ret = str(float(kg.group(0)) * 1000)
		return ret

	def __setAgeCategory__(self, line):
		# Formats age category
		ret = ""
		categories = ["egg", "stilbor", "nymph", "pupa", "placenta"]
		cat = line[self.header["Age Cat"]].lower().strip()
		if not cat:
			cat = line[self.header["Age (y.m)"]].lower().strip()
		if cat:
			if cat == "ad" or "adult" in cat:
				ret = "adult"
			elif cat == "juv" or "juvenile" in cat:
				ret = "juvenile"
			elif cat == "neon" or "neonat" in cat:
				# Omit e to account for neonatal
				ret = "neonate"
			elif cat == "tpole" or "tadpole" in cat:
				cat = "tadpole"
			else:
				for i in categories:
					if cat == i:
						ret = i
		return ret

	def __setComments__(self, line):
		# Merges weight and diagnosis coulmns
		ret = ""
		cat = self.__setAgeCategory__(line)
		weight = self.__setWeight__(line).strip()
		if cat:
			ret += "{}. ".format(cat)
		if weight:
			ret += "Weight: {}. ".format(weight)
		diag = ["GD:", "FD:", "Frozen", "Formalin"]
		for i in diag:
			val = line[self.header[i]].strip()
			if val:
				if val[-1] != ".":
					val += "."
				ret += " "
				ret += val
		return ret.strip()

	def __setAge__(self, line):
		# Converts age to months
		ret = ""
		age = line[self.header["Age (y.m)"]].lower().strip()
		if not age:
			age = line[self.header["Age Cat"]].lower().strip()
		if age:
			age = age.replace(";", "")
			val = 0
			for idx, i in enumerate([self.years, self.months, self.days]):
				match = i.search(age)
				if match:
					d = self.__removePunctuation__(match.group(1))
					d = float(d)
					if i == 0:
						val += d * 12
					elif i == 1:
						val += d
					else:
						val += d / 30
			ret = str(val)
		return str(ret)

	def __setSex__(self, line):
		# Formats set
		ret = ""
		sex = line[self.header["Sex"]].lower()
		if sex == "m":
			ret = "male"
		elif ret == "f":
			ret = "female"
		return ret

	def __formatLine__(self, line):
		# Parses and formats individual line
		ret = []
		ret.append(line[self.header["Common Name"]].strip())
		ret.append(line[self.header["Scientific name"]].strip())
		ret.append(self.__setAge__(line))
		ret.append(self.__setSex__(line))
		ret.append(line[self.header["PM/Dth Date"]].strip())
		ret.append(line[self.header["Year"]].strip())
		ret.append(self.__setComments__(line))
		ret.append(self.__setAccount__(line))
		return ret

	def format(self):
		# Preformats London zoo data
		with open(self.outfile, "w") as out:
			print("\n\tFormatting London Zoo data...")
			out.write(self.outheader)
			for line in readFile(self.infile):
				if not self.header:
					self.header = line
				else:
					row = self.__formatLine__(line)
					out.write(",".join(row) + "\n")

def main():
	start = datetime.now()
	parser = ArgumentParser("Preformats London Zoo data before parsing by compOncDB.")
	parser.add_argument("i", help = "Path to London Zoo csv.")
	l = LondonZoo(parser.parse_args())
	l.format()
	print(("\tTotal runtime: {}\n").format(datetime.now() - start))

if __name__ == "__main__":
	main()
