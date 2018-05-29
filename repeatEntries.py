'''This script will attempt to identify entries from NWZP which have 
multiple entries over time.'''

import os
from argparse import ArgumentParser

def getColumns(head):
	# Returns dict of column numbers
	col = {"name":-1,"pid":-1,"cid":-1,"account":-1,"id":-1}
	for idx,i in enumerate(head):
		i = i.strip().lower
		if i == "patient":
			col["pid"] = idx
		elif i == "pt_name":
			col["name"] = idx
		elif i == "caseid":
			col["cid"] = idx
		elif i == "account":
			col["account"] = idx
		elif i == "id":
			col["id"] = idx
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

def getRepeats(infile):
	# Returns list of repeated entries
	entries = {}
	reps = []
	first = True
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				spli = line.split(delim)
				

			else:
				first = False
				delim = getDelim(line)
				col = getColumns(line.split(delim))

def checkArgs(args):
	# Check args for errors
	if not args.i or not args.o:
		print(\n\t"[Error] Please specify input and output files. Exiting.\n")
		quit()
	if not os.path.isfile(args.i):
		print(("\n\t[Error] Cannot find {}. Exiting.\n").format(args.i))
		quit()

def main():
	parser = ArgumentParser("This script will attempt to identify entries \
from NWZP which have multiple entries over time.")
	parser.add_argument("-i", help = "Path to NWZP file.")
	parser.add_argument("-o", help = "Path to output file")
	args = parser.parse_args()
	checkArgs(args)
	reps = getRepeats(args.i)
	extractRepeats(args.i. args.o, reps)

if __name__ == "__main__":
	main()
