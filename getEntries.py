'''This script can be used to count the number of unique entries found in a given 
column of a file, extract values from a given column, or identify multiple entries.'''

import os
from argparse import ArgumentParser
from vetPathUtils import printError, getDelim

def getColumn(col, row):
	# Returns target column number
	try:
		# Return col if it is already and integer
		int(col)
		return col
	except ValueError:
		# Identify column number
		for idx, i in enumerate(row):
			i = i.strip()
			if i == col:
				return idx
	printError("Cannot find target column number.")

def findMatch(c, vals):
	# Identifies whole word matches
	if c in vals:
		return True
	if len(vals) == 1:
		# Attwmpt to isolate match
		s = c.split()
		for i in s:
			if i == vals[0]:
				return True
	return False

def readList(infile):
	# Returns list of search values
	vals = []
	with open(infile, "r") as f:
		for line in f:
			s = line.strip().split(",")[0]
			vals.append(s)
	return vals

def extractLines(negate, infile, c, val, outfile=None):
	# Counts unique entries in col
	first = True
	total = 0
	matches = []
	if os.path.isfile(val):
		vals = readList(val)
	else:
		vals = [val]
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				total += 1
				spli = line.split(delim)
				if len(spli) > col:
					match = findMatch(spli[col].strip(), vals)
					if match == True and negate == False:
						matches.append(line)
					elif match == False and negate == True:
						matches.append(line)
			else:
				delim = getDelim(line)
				col = getColumn(c, line.split(delim))
				matches.append(line)
				first = False
	if outfile:
		with open(outfile, "a") as out:
			for i in matches:
				out.write(i)
	return len(matches)-1, total

def countUnique(infile, c):
	# Counts unique entries in col
	x = set()
	first = True
	total = 0
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				total += 1
				spli = line.split(delim)
				if len(spli) > col:
					x.add(spli[col])
			else:
				first = False
				delim = getDelim(line)
				col = getColumn(c, line.split(delim))
	return x, total

def getTarget(infile, outfile, c, target=None):
	# Write entries from col with values in target to file (writes lines with no entry is target is null)
	total = 0
	count = 0
	first = True
	with open(outfile, "a") as out:
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					write = False
					total += 1
					spli = line.strip().split(delim)
					if len(spli) >= col:
						n = spli[col]
						if target and n in target:
							# Write line if value is in target
							write = True
						elif len(n) < 1:
							# Write line with missing entry
							write = True
						if write == True:
							out.write(line)
							count += 1
				else:
					delim = getDelim(line)
					col = getColumn(c, line.split(delim))
					first = False
	return count, total

def identifyMultiples(infile, c):
	# Returns a lsit of non-unique col entries
	entries = {}
	mult = []
	first = True
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				spli = line.strip().split(delim)
				if len(spli) >= col:
					# Count entry occurances
					if spli[col] in entries.keys():
						entries[spli[col]] += 1
					else:
						entries[spli[col]] = 1
			else:
				delim = getDelim(line)
				col = getColumn(c, line.split(delim))
				first = False
	for i in entries.keys():
		if entries[i] > 1:
			# Get multiple occurances
			mult.append(i)
	return mult

def checkArgs(args):
	# Identifies errors in arguments
	if not args.i:
		printError("Please provide an input file")
	if not args.c:
		args.c = input("\n\tPlease enter column name or number: ")
	if args.multiple == True or args.empty == True:
		if args.v:
			print("\n\t[Warning] Ignoring -v argument.\n")
		if not os.path.isfile(args.o):
			# Initialize output file with header
			with open(args.o, "w") as out:
				with open(args.i, "r") as f:
					head = f.readline()
				out.write(head)

def main():
	parser = ArgumentParser("This script can be used to count the number of \
unique entries found in a given column of a file, extract values from a given column, or identify multiple entries.")
	parser.add_argument("--negate", action = "store_true", default = False,
help = "Identify entries that do not equal values.")
	parser.add_argument("-c", help = "Name or number of column to analyze.")
	parser.add_argument("-v", help = "Value (or file with list of values) from column c to extract (leave blank to count).")
	parser.add_argument("--multiple", action = "store_true", default = False,
help = "Writes entries with multiple occurances from column c to output file (will append to existing output file).")
	parser.add_argument("--empty", action = "store_true", default = False,
help = "Writes entries with no entry in column c to output file (will append to existing output file).")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Path to output file (omit for counting).")
	args = parser.parse_args()
	checkArgs(args)
	if args.multiple or args.empty:
		if args.multiple == True:
			print(("\n\tIdentifying multiple entries from column {}...").format(args.c))
			target = identifyMultiples(args.i, args.c)
			x, t = getTarget(args.i, args.o, args.c, target)
			print(("\n\tIdentified {} multiple entries from {} total entries.\n").format(x, t))
		elif args.empty == True:
			print(("\n\tIdentifying null entries from column {}...").format(args.c))
			x, t = getTarget(args.i, args.o, args.c)
			print(("\n\tIdentified {} entries with missing values from {} total entries.\n").format(x, t))
	elif args.v:
		if os.path.isfile(args.v):
			msg = "in " + args.v
		else:
			msg = "equal to " + args.v
		print(("\n\tExtracting entries with column {} {}...").format(args.c, msg))
		x, t = extractLines(args.negate, args.i, args.c, args.v, args.o)
		print(("\tExtracted {:,} entries from {:,} total entries.\n").format(x, t))
	else:
		print(("\n\tGetting unique entries from column {}...").format(args.c))
		x, t = countUnique(args.i, args.c)
		print(("\tFound {:,} unique entries from {:,} total entries.\n").format(len(x), t))

if __name__ == "__main__":
	main()
