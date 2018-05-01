'''This script can be used to count the number of unique entries found in a given column of a file'''

from argparse import ArgumentParser

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
				delim = None
				for i in ["\t", ",", " "]:
					if i in line:
						delim = i
						break
				if not delim:
					print("\n\t[Error] Cannot determine delimeter. Check file formatting. Exiting.\n")
					quit()
	return x, total

def main():
	parser = ArgumentParser("This script can be used to count the number of \
unique entries found in a given column of a file")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-c", type = int, default = -1,
help = "Column  number to analyze.")
	args = parser.parse_args()
	if args.c == -1:
		args.c = input("\n\tPlease enter column number: ")
	print(("\n\tGetting unique entries from column {}...").format(args.c))
	x, t = countUnique(args.i, args.c)
	print(("\tFound {} unique entries from {} total entries.\n").format(len(x), t))

if __name__ == "__main__":
	main()
