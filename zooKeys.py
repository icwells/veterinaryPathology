'''This script will generate unique keys for zoos in NWZP'''

from argparse import ArgumentParser

def insertKeys(keys, infile, outfile):
	# Inserts keys into new infile
	first = True
	with open(outfile, "w") as out:
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					s = line.split("\t")
					n = s[1].strip()
					if n in keys.keys():
						k = keys[n]
					else:
						k = "NA"
					l = [s[0], k]
					l.extend(s[2:])
					out.write(("\t").join(l))
				else:
					out.write(line)
					first = False

def readKeys(infile):
	# Reads in dict of keys
	first = True
	keys = {}
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				s = line.split("\t")
				if len(s) == 2:
					keys[s[0]] = s[1].strip()
			else:
				first = False
	return keys

def getKeys(zoos, outfile):
	# Generates unique identifiers for each entry in zoos
	keys = {}
	with open(outfile, "w") as out:
		out.write("Account, Key\n")
		for idx,i in enumerate(zoos):
			key = ("nwzp{}").format(idx+1)
			out.write(("{}\t{}\n").format(i, key))
			keys[key] = i
	return keys

def getAccounts(infile):
	# Returns unique account names
	first = True
	zoos = set()
	with open(infile, "r") as f:
		for line in f:
			s = line.split("\t")
			if first == False:
				n = s[c].strip()
				if n:
					zoos.add(n)
			else:
				first = False
				for idx,i in enumerate(s):
					if i.strip().lower() == "account":
						c = idx
						break
	return list(zoos)

def main():
	parser = ArgumentParser("This script will generate unique keys for zoos in NWZP")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-k", help = "Path to key file (inserts keys into outfile).")
	parser.add_argument("-o", help = "Path to output file.")
	args = parser.parse_args()
	if args.k:
		keys = readKeys(args.k)
		insertKeys(keys, args.i, args.o)
	else:
		zoos = getAccounts(args.i)
		getKeys(zoos, args.o)

if __name__ == "__main__":
	main()
