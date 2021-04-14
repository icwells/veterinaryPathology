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
		self.days = re.compile(r"([0-9]+)\s?(d|day)")
		self.count = 0
		self.digits = re.compile(digits)
		self.header = None
		self.infile = args.i
		self.months = re.compile(r"([0-9]+)\s?(m|mnths|month)")
		self.outfile = join(split(self.infile)[0], "LondonZoo.Preformatted.csv")
		self.outheader = "ID,CommonName,ScientificName,Age,Sex,Date,Year,Comments,Account\n"
		self.total = 0
		self.years = re.compile("{}\s?(y|yrs|year)".format(digits))

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
			ret = g.group(0) + " g"
		else:
			kg = self.digits.search(line[self.header["Wt - kg"]])
			if kg:
				ret = str(float(kg.group(0)) * 1000) + " g"
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

#-----------------------------------------------------------------------------

	def __removePunctuation__(self, val):
		# Removes leading punctuation marks
		if val and val[0] in punctuation:
			val = val[1:]
		return float(val)

	def __getMatch__(self, term, age):
		# Returns regex match
		match = term.search(age)
		if match:
			return self.__removePunctuation__(match.group(1))
		return 0.0

	def __setAge__(self, line):
		# Converts age to months
		age = line[self.header["Age (y.m)"]].lower().strip()
		#if not age:
		#	age = line[self.header["Age Cat"]].lower().strip()
		if age:
			age = age.replace(";", "")
			ret = self.__getMatch__(self.years, age)
			ret += self.__getMatch__(self.months, age) / 12
			ret += self.__getMatch__(self.days, age) / 365
			if ret > 0:
				return str(ret)
		return ""

	def __setSex__(self, line):
		# Formats set
		ret = ""
		sex = line[self.header["Sex"]].lower()
		if sex == "m":
			ret = "male"
		elif ret == "f":
			ret = "female"
		return ret

	def __checkSpecies__(self, line):
		# Removes vague terms from species names
		name = line[self.header["Scientific name"]].strip()
		sp = name.split()
		if len(sp) > 1:
			if sp[1] == "sp" or sp[1] == "sp." or sp[1] == "spp":
				name = sp[0]
		return name

	def __formatLine__(self, line):
		# Parses and formats individual line
		ret = []
		self.count += 1
		ret.append(str(self.count))
		ret.append(line[self.header["Common Name"]].strip())
		ret.append(self.__checkSpecies__(line))
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
