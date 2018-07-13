'''This script will attempt to identify entries from NWZP which have 
multiple entries over time.'''

import os
from argparse import ArgumentParser
from datetime import datetime

class Entries():
	# Class for identifying repeated patient ids 
	def __init__(self):
		self.IDs = set()
		self.Reps = set()

	def Add(self, pid):
		# Stores unique entries in sets
		if pid in self.IDs:
			self.Reps.add(pid)
		else:
			self.IDs.add(pid)

class Sorter():
	# Class for sorting and filtering repeated patient ids
	def __init__(self):
		# Hierachical dict: {client: {pid: {patient:set(date)}}
		self.IDs = {}
		self.Total = 0

	def Add(self, pid, patient, date, client):
		# Adds data to hierarchical dict
		patient = patient.lower().strip()
		client = client.lower().strip()
		if client not in self.IDs.keys():
			# Initialize client dict
			self.IDs[client] = {}
		if patient not in self.IDs[client].keys():
			# Initialize species name entry
			self.IDs[client][patient] = {}
		if pid not in self.IDs[client][patient].keys():
			# Initialize patient id name entry
			self.IDs[client][patient][pid] = set()
		self.IDs[client][patient][pid].add(date.strip())

	def Sort(self):
		# Removes non-unique repeats
		for k in self.IDs.keys():
			for p in self.IDs[k].keys():
				keys = list(self.IDs[k][p].keys())
				for i in keys:
					if i in self.IDs[k][p].keys():
						if len(self.IDs[k][p][i]) <= 1:
							del self.IDs[k][p][i]
						else:
							self.IDs[k][p][i] = list(self.IDs[k][p][i])
							self.Total += len(self.IDs[k][p][i])

	def GetMatch(self, pid, date, patient, client):
		# Returns true if client and patient match, and date in u
		patient = patient.lower().strip()
		client = client.lower().strip()
		if client in self.IDs.keys():
			if patient in self.IDs[client].keys():
				if pid in self.IDs[client][patient].keys():
					if date in self.IDs[client][patient][pid]:
						return True
		return False

#-----------------------------------------------------------------------------

def getColumns(head):
	# Returns dict of column numbers
	col = {"pid":-1,"date":-1,"name":-1,"client":-1}
	for idx,i in enumerate(head):
		i = i.strip().lower()
		if i == "patient":
			col["pid"] = idx
		elif i == "client":
			col["client"] = idx
		elif i == "pt_name":
			col["name"] = idx
		elif i == "date_rcvd":
			col["date"] = idx
	for i in col.keys():
		if col[i] == -1:
			print(("[Error] Could not find column index for {}. Exiting.\n").format(i))
			quit()
	# Store max value to avoid index errors
	col["max"] = max(list(col.values()))
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
					if len(spli) >= col["max"]:
						pid = spli[col["pid"]]
						date = spli[col["date"]].strip()
						name = spli[col["name"]]
						client = spli[col["client"]]
						if reps.GetMatch(pid, date, name, client) == True:
							out.write(line)
				else:
					# Write header without editting
					out.write(line)
					first = False

def getUnique(infile, reps, delim, col):
	# Identifies repeated elements with multiple unique entries
	s = Sorter()
	first = True
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				spli = line.split(delim)
				if len(spli) >= col["max"]:
					pid = spli[col["pid"]]
					if pid in reps:
						s.Add(pid, spli[col["name"]], spli[col["date"]], spli[col["client"]])
			else:
				first = False
	s.Sort()
	return s

def getRepeats(infile):
	# Returns list of repeated entries
	entries = Entries()
	first = True
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				spli = line.split(delim)
				if len(spli) >= c and spli[c].strip():
					# Add id to respective set
					entries.Add(spli[c])
			else:
				first = False
				delim = getDelim(line)
				col = getColumns(line.split(delim))
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
	print(("\tIdentified {} repeated patient IDs.").format(len(reps)))
	print("\n\tSorting repeated patient IDs...")
	unique = getUnique(args.i, reps, delim, col)
	print(("\tIdentified {} repeated patient entries.").format(unique.Total))
	print("\n\tExtracting repeated entries...")
	extractRepeats(args.i, args.o, unique, delim, col)
	print(("\tFinished. Runtime: {}\n").format(datetime.now()-start))

if __name__ == "__main__":
	main()
