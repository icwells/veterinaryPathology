'''Attempts to identify suspect cases in upload file.'''

from argparse import ArgumentParser
from copy import deepcopy
from datetime import datetime
import unixpath

class SuspectCases():

	def __init__(self, args):
		self.cases = {}
		self.columns = ["Sex", "Age", "ID", "Species", "Name", "Date", "Year", "Comments", "TumorType", "Location"]
		self.d = ","
		self.outfile = args.o
		self.suspect = {}
		print()
		for i in [args.s, args.c]:
			self.__setCases__(i)
		self.__identifySuspect__(args.i)

	def __setCases__(self, infile):
		# Stores cases by species in dict
		first = True
		print("\tReading {}...".format(infile))
		for i in unixpath.readFile(infile, d = self.d):
			if not first:
				if i[h["MassPresent"]] == "1":
					t = i[h["Species"]].strip()
					if t not in self.cases.keys():
						self.cases[t] = []
					row = []
					for c in self.columns:
						row.append(i[h[c]])
					self.cases[t].append(row)
			else:
				h = i
				first = False

	def __identifySuspect__(self, infile):
		# Attempts to identify suspect cases
		count = 0
		first = True
		print("\tIdentifying suspect cases...")
		with open(self.outfile, "w") as out:
			for i in unixpath.readFile(infile, d = self.d):
				if not first:
					t = i[h["Taxa"]].strip()
					if t.count(" ") > 1:
						# Remove subspecies name
						t = " ".join(t.split()[:2])
					if t in self.cases.keys():
						name = i[h["Common_Name"]].strip()
						sex = i[h["Sex"]].strip()
						date = i[h["Death_Date"]].strip()
						if sex != "male" and sex != "female":
							sex = "NA"
						#diag = i[h["Diagnosis"]].strip()
						#loc = i[h["Neoplasia_location"]].strip()
						for r in self.cases[t]:
							if date == r[5].replace(".", "/"):
							#if r[0] == sex or r[4] == name:
								row = deepcopy(r)
								row.extend(i)
								out.write(self.d.join(row) + "\n")
								count += 1
				else:
					h = i
					first = False
					head = deepcopy(self.columns)
					tail = [""] * len(h)
					for k in i.keys():
						tail[h[k]] = k
					head.extend(tail)
					out.write(self.d.join(head) + "\n")
		print("\tFound {} potential records.".format(count))

def main():
	start = datetime.now()
	parser = ArgumentParser("Attempts to identify suspect cases in upload file.")
	parser.add_argument("-c", help = "Path to common name upload file.")
	parser.add_argument("-i", help = "Path to suspect records input file.")
	parser.add_argument("-o", help = "Path to output file.")
	parser.add_argument("-s", help = "Path to scientific name upload file.")
	SuspectCases(parser.parse_args())
	print(("\tTotal runtime: {}\n").format(datetime.now() - start))

if __name__ == "__main__":
	main()
