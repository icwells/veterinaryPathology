'''This script will extract summary data for species at least 100 records'''

from argparse import ArgumentParser
from datetime import datetime
from unixpath import *
from vetPathUtils import *

def recordEntry():
	# Returns new entry for record dict
	return {"total":0, "cancer":0, "male":0, "female":0, "age":0.0}

def writeRecords(outfile, records):
	# Writes dict to file
	print("\tWriting records to file...")
	with open(outfile, "w") as out:
		out.write("ScientificName,TotalRecords,CancerRecords,CancerRate,AverageAge(months),Male:Female\n")
		for i in records.keys():
			rate = records[i]["cancer"]/records[i]["total"]
			age = records[i]["age"]/records[i]["total"]
			sex = records[i]["male"]/records[i]["female"]
			row = ("{},{},{},{:.2%},{:.2f},{:.2f}\n").format(i, records[i]["total"], records[i]["cancer"], rate, age, sex)
			out.write(row)

def getSpeciesSummaries(infile, species, col, d):
	# Returns dict of species totals, cancer rates, # male/female, etc
	first = True
	records = {}
	print("\tGetting records...")
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				spl = line.strip().split(d)
				n = spl[col.Species]
				if n in species:
					if n not in records.keys():
						records[n] = recordEntry()
					# Update total, cancer rate, age, and sex
					records[n]["total"] += 1
					try:
						records[n]["age"] += float(spl[col.Age])
					except ValueError:
						pass
					if "8" in spl[col.Code]:
						records[n]["cancer"] += 1
					if spl[col.Sex].lower().strip() == "male":
						records[n]["male"] += 1
					elif spl[col.Sex].lower().strip() == "female":
						records[n]["female"] += 1
			else:
				first = False
	return records

def getTargetSpecies(infile):
	# Returns list of species with at least 100 entries
	totals = {}
	species = []
	first = True
	print("\n\tGetting species totals...")
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				spl = line.split(d)
				n = spl[col.Species]
				# Count number of occurances
				if n in totals.keys():
					totals[n] += 1
				else:
					totals[n] = 1
			else:
				d = getDelim(line)
				col = Columns(line.split(d))
				first = False
	for i in totals.keys():
		if totals[i] >= 100:
			species.append(i)
	return species, col, d

def checkArgs(args):
	# Check args for errors
	if not args.i or not args.o:
		printError("Please specify input and output files")
	if not os.path.isfile(args.i):
		printError(("Cannot find {}").format(args.i))

def main():
	start = datetime.now()
	parser = ArgumentParser(
"This script will extract summary data for species at least 100 records.")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Path to output csv.")
	args = parser.parse_args()
	checkArgs(args)
	species, col, d = getTargetSpecies(args.i)
	records = getSpeciesSummaries(args.i, species, col, d)
	writeRecords(args.o, records)
	printRuntime(start)

if __name__ == "__main__":
	main()
