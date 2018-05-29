'''This script will count the number of cancer occurances per species and per database.'''

from datetime import datetime
from argparse import ArgumentParser
from copy import deepcopy

def getPercent(count, total):
	# Returns formatted percentage if possible
	if count == "NA" and total == "NA":
		return "NA"
	else:
		if type(count) == int and type(total) == int:
			percent = float(count)/total
			return ("{:.1%}").format(percent)

def extendOutput(o, d, n):
	# Extends output list if n is in d.keys()
	if n in d.keys():
		o.extend([d[n]["c"], d[n]["o"], d[n]["t"], getPercent(d[n]["c"], d[n]["t"])])
	else:
		o.extend(["NA", "NA", "NA", "NA"])
	return o

def addDicts(total, d):
	# Adds number of occurances in d to total 
	for i in d:
		if not i in total.keys():
			total[i] = deepcopy(d[i])
		else:
			total[i]["c"] += d[i]["c"]
			total[i]["o"] += d[i]["o"]
			total[i]["t"] += d[i]["t"]
		if "com" not in total[i].keys():
			if  "com" in d[i].keys():
				total[i]["com"] = d[i]["com"]
			else:
				total[i]["com"] = ""
	return total

def mergeOccurances(outfile, nwzp, zeps, msu):
	# Compares data found in all databases
	total = {}
	print("\n\tComparing all databases...")
	total = addDicts(total, nwzp)
	total = addDicts(total, zeps)
	total = addDicts(total, msu)
	print(("\tFound records for {} unique species.").format(len(total.keys())))
	countOccurances(total)
	print("\n\tWriting output...")
	with open(outfile, "w") as output:
		output.write("ScientificName,CommonName,Totalcancer,Totalother,Totaltotal,Total%,\
NWZPcancer,NWZPother,NWZPtotal,NWZP%,ZEPScancer,ZEPSother,ZEPStotal,ZEPS%,MSUcancer,MSUother,MSUtotal,MSU%\n")
		for i in total.keys():
			o = [i, total[i]["com"], total[i]["c"], total[i]["o"], total[i]["t"], getPercent(total[i]["c"], total[i]["t"])]
			for d in [nwzp, zeps, msu]:
				o = extendOutput(o, d, i)
			string = [str(x) for x in o]
			output.write(",".join(string) + "\n")

def countOccurances(species):
	# Returns total species with and without cancer
	cancer = 0
	other = 0
	for i in species.keys():
		if species[i]["c"] > 0:
			cancer += 1
		elif species[i]["o"] > 0:
			other += 1
	print(("\tFound {} species with cancer reported and {} species with no cases \
reported").format(cancer, other))

def getOccurances(infile, diag=False):
	# Counts number of unique cancer occurances by species
	species = {}
	first = True
	name = -1
	com = -1
	code = -1
	with open(infile, "r") as f:
		for line in f:
			line = line.strip().split(",")
			if first == False and len(line) >= name:
				n = line[name].strip()
				if n and n.lower() != "na":
					if "et al" in n.lower() or n.lower()[:2] == "na ":
						pass
					else:
						if n not in species.keys():
							# {name: {# cancer occurances, # occurances without cancer}}
							species[n] = {"com":"","c":0, "o":0, "t":0}
						if not species[n]["com"]:
							species[n]["com"] = line[com].strip()
						if diag == True and len(line) >= code:
							# Get total with and without cancer
							species[n]["t"] += 1
							if "8" in line[code]:
								species[n]["c"] += 1
							else:
								species[n]["o"] += 1
						else:
							# Count all occurnaces as cancer
							species[n]["c"] += 1
							species[n]["t"] += 1
			else:
				# Get target column numbers
				for idx,i in enumerate(line):
					if i == "ScientificName":
						name = idx
					if i == "CommonName" or i == "Breed":
						com = idx
					if diag == True:
						if i == "Code":
							code = idx
				if name == -1 or com == -1:
					print(("\n\t[Error] Could not find scientific or common name columns ({}, {}). Exiting.\n").format(name, com))
					quit()
				if diag == True and code == -1:
					print(("\n\t[Error] Could not find diagnosis code column. Exiting.\n").format(code))
					quit()	
				first = False
	print(("\tFound records for {} unique species.").format(len(species.keys())))
	if diag == True:
		countOccurances(species)		
	return species

def getZEPSoccurances(infile):
	# Reads Drury/ZEPS species count data
	species = {}
	first = True
	with open(infile, "r") as f:
		for line in f:
			spli = line.strip().split(",")
			if first == False:
				if len(spli) >= col:
					n = spli[col]
					if n != "NA":
						other = int(spli[2])-int(spli[1])
						species[n] = {"c":int(spli[1]), "o":other, "t":int(spli[2])}
			else:
				for idx,i in enumerate(spli):
					if i.strip() == "ScientificName":
						col = idx
						break
				first = False
	return species

def main():
	start = datetime.now()
	parser = ArgumentParser("This script will count the number of cancer \
occurances per species and per database.")
	parser.add_argument("-n", help = "Path to NWZP file.")
	parser.add_argument("-m", help = "Path to merged MSU file.")
	parser.add_argument("-z", help = "Path to ZEPS species count file (with scientific names).")
	parser.add_argument("-o", help = "Path to output file.")
	args = parser.parse_args()
	print("\n\tGetting NWZP data...")
	nwzp = getOccurances(args.n, True)
	print("\n\tGetting ZEPS data...")
	zeps = getZEPSoccurances(args.z)
	print("\n\tGetting MSU data...")
	msu = getOccurances(args.m)
	mergeOccurances(args.o, nwzp, zeps, msu)
	print(("\tFinished. Runtime: {}\n").format(datetime.now()-start))

if __name__ == "__main__":
	main()
