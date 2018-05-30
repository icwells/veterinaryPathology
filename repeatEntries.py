'''This script will attempt to identify entries from NWZP which have 
multiple entries over time.'''

import os
from argparse import ArgumentParser
from datetime import datetime

class Entries():
	# Class for storing 
	def __init__(self):
		self.IDs = set()
		self.Reps = set()

	def Add(self, pid):
		# Stores unique entries in dicts of sets
		if pid in self.IDs:
			self.Reps.add(pid)
		else:
			self.IDs.add(pid)

#-----------------------------------------------------------------------------

def getColumns(head):
	# Returns dict of column numbers
	col = {"pid":-1,"cid":-1,"date":-1}
	for idx,i in enumerate(head):
		i = i.strip().lower()
		if i == "patient":
			col["pid"] = idx
		elif i == "caseid":
			col["cid"] = idx
		elif i == "date_rcvd":
			col["date"] = idx
	for i in col.keys():
		if col[i] == -1:
			print(("[Error] Could not find column index for {}. Exiting.\n").format(i))
			quit()
	return col

def getDelim(line):
	# Returns delimiter
	for i in ["\t", ",", " "]:
		if i in line:
			return i
	print("\n\t[Error] Cannot determine delimeter. Check file formatting. Exiting.\n")
	quit()

def extractRepeats(infile, outfile, reps, delim, col):
	# Writes entries in reps to file
	first = True
	with open(outfile, "w") as out:
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					spli = line.split(delim)
					if len(spli) >= col:
						if spli[col] in reps:
							out.write(line)
				else:
					# Write header without editting
					out.write(line)
					first = False

def getUnique(infile, reps, delim, col):
	# Identifies repeated elements with multiple unique entries
	unique = {}
	first = True
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				
			else:
				first = True

def getRepeats(infile):
	# Returns list of repeated entries
	entries = Entries()
	first = True
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				spli = line.split(delim)
				if len(spli) >= c and spli[c].strip():
					# Add fields to respective dicts
					entries.Add(spli[c])
			else:
				first = False
				delim = getDelim(line)
				col = getColumns(line)
				c = col["pid"]
	return list(entries.Reps), delim, col

def checkArgs(args):
	# Check args for errors
	if not args.i or not args.o:
		print("\n\t[Error] Please specify input and output files. Exiting.\n")
		quit()
	if not os.path.isfile(args.i):
		print(("\n\t[Error] Cannot find {}. Exiting.\n").format(args.i))
		quit()

def main():
	start = datetime.now()
	parser = ArgumentParser("This script will attempt to identify entries \
from NWZP which have multiple entries over time.")
	parser.add_argument("-i", help = "Path to NWZP file.")
	parser.add_argument("-o", help = "Path to output file")
	args = parser.parse_args()
	checkArgs(args)
	print("\n\tIdentifying repeated entries...")
	reps, delim, col = getRepeats(args.i)
	print("\tSorting repeated patient IDs...")
	unique = getUnique(args.i, reps, delim, col)
	print("\tExtracting repeated entries...")
	extractRepeats(args.i, args.o, unique, delim, col)
	print(("\tFinished. Runtime: {}\n").format(datetime.now()-start))

if __name__ == "__main__":
	main()
