'''This script will assemble an upload file for the comparative oncology database'''

import os
from argparse import ArgumentParser
from vetPathUtils import *

def subsetLine(idx, line):
	# Returns line item if index is valid
	ret = "NA"
	if idx is not None and idx < len(line) and line[idx].strip():
		ret = line[idx]
	return ret

def getBinary(idx, line):
	# Returns SMALLINT value for binary fields
	val = subsetLine(idx, line)
	if val == "Y" or val == "yes":
		return "1"
	elif val == "N" or val == "No":
		return "0"
	else:
		return "-1"

def checkAge(idx, line):
	# Returns -1 if age is na
	age = subsetLine(idx, line)
	if age.upper() == "NA" or len(age) > 7:
		# Return -1 if age is too long (age would be impossible)
		return "-1"
	else:
		try:
			a = float(age)
			return age
		except ValueError:
			return "-1"

def checkID(idx, line):
	# Makes sure source ID is an integer
	val = subsetLine(idx, line)	
	try:
		i = int(val)
		return val
	except ValueError:
		return "-1"

def checkSex(idx, line):
	# Returns male/female/NA
	val = subsetLine(idx, line)
	if val != "NA":
		val = val.lower()
		if val != "male" and val != "female":
			if val == "m":
				val = "male"
			elif val == "f":
				val = "female"
	return val	

def formatLine(col, line):
	# Return line formatted for writing to outfile
	row = []
	if len(line) >= col.Max and line[col.Species].upper() != "NA":
		row.append(checkSex(col.Sex, line))
		row.append(checkAge(col.Age, line))
		row.append(getBinary(col.Castrated, line))
		row.append(checkID(col.ID, line))
		row.append(subsetLine(col.Species, line))
		row.append(subsetLine(col.Date, line))
		row.append(subsetLine(col.Comments, line))
		# Masspresent
		if line[col.Type] != "NA":
			row.append("1")
		else:
			row.append("0")
		row.append(getBinary(col.Necropsy, line))
		row.append(getBinary(col.Metastasis, line))
		row.append(subsetLine(col.Type, line))
		row.append(subsetLine(col.Location, line))
		row.append(getBinary(col.Primary, line))
		row.append(getBinary(col.Malignant, line))
		row.append(col.Service)
		row.append(subsetLine(col.Account, line))
		row.append(subsetLine(col.Submitter, line))
	return ",".join(row)

def checkOutfile(outfile):
	# Creates file if it does not exist
	if not os.path.isfile(outfile):
		with open(outfile, "w") as out:
			# Write header
			out.write("Sex,Age,Castrated,ID,Species,Date,Comments,MassPresent,Necropsy,\
Metastasis,TumorType,Location,Primary,Malignant,Service,Account,Submitter\n")

def parseRecords(infile, outfile):
	# Sorts input and re-writes according to upload template
	first = True
	count = 0
	total = 0
	serv = getService(infile)
	checkOutfile(outfile)
	with open(outfile, "a") as out:
		with open(infile, "r") as f:
			for line in f:
				line = line.strip()
				if first == False:
					total += 1
					spl = line.split(d)
					res = formatLine(col, spl)
					if res:
						out.write(res + "\n")
						count += 1
				else:
					d = getDelim(line)
					col = Columns(line.split(d), serv)
					first = False
	print(("\tExtracted {} records from {} total records.\n").format(count, total))

def main():
	parser = ArgumentParser(
"This script will assemble an upload file for the comparative oncology database.")
	parser.add_argument("-i", help = "Path to full record file.")
	parser.add_argument("-o", help = "Path to output csv (will append to existing file).")
	args = parser.parse_args()
	print(("\n\tSorting data from {}...").format(args.i))
	parseRecords(args.i, args.o)

if __name__ == "__main__":
	main()
