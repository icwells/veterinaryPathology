'''This script can be used to count the number of unique entries found in a given column 
of a file or to extract values from a given column.'''

from argparse import ArgumentParser

def getDelim(line):
	# Returns delimiter
	for i in ["\t", ",", " "]:
		if i in line:
			return i
	print("\n\t[Error] Cannot determine delimeter. Check file formatting. Exiting.\n")
	quit()

def extractLines(infile, outfile, col, val):
	# Counts unique entries in col
	x = 0
	first = True
	total = 0
	with open(outfile, "w") as output:
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					total += 1
					spli = line.split(delim)
					if len(spli) > col and spli[col].strip() == val:
						output.write(line)
						x += 1
				else:
					output.write(line)
					first = False
					delim = getDelim(line)
	return x, total

def countUnique(infile, col):
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
	return x, total

def main():
	parser = ArgumentParser("This script can be used to count the number of \
unique entries found in a given column of a file or to extract values from a given column.")
	parser.add_argument("-c", type = int, default = -1,
help = "Column  number to analyze.")
	parser.add_argument("-v", help = "Value from column c to extract (leave blank to count).")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Path to output file (if extracting).")
	args = parser.parse_args()
	if args.c == -1:
		args.c = input("\n\tPlease enter column number: ")
	if args.v:
		print(("\n\tExtracting entries with column {} equal to {}...").format(args.c, args.v))
		x, t = extractLines(args.i, args.o, args.c, args.v)
		print(("\tExtracted {} entries from {} total entries.\n").format(x, t))
	else:
		print(("\n\tGetting unique entries from column {}...").format(args.c))
		x, t = countUnique(args.i, args.c)
		print(("\tFound {} unique entries from {} total entries.\n").format(len(x), t))

if __name__ == "__main__":
	main()
