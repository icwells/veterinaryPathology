'''This script will assemble an upload file for the comparative oncology database'''

import os
from argparse import ArgumentParser
from vetPathUtils import *

def getBinary(val):
	# Returns SMALLINT value for binary fields
	if val == "Y":
		return "1"
	elif val == "N":
		return "0"
	else:
		return "-1"

def formatLine(col, line):
	# Return line formatted for writing to outfile
	row = []
	if len(line) >= col.Max:
		row.append(line[col.Sex])
		row.append(line[col.Age])
		row.append(getBinary(line[col.Castrated]))
		row.append(line[col.ID])
		row.append(line[col.Species])
		row.append(line[col.Date])
		row.append(line[col.Comments])
		# Masspresent
		if line[col.Type] != "NA":
			row.append("1")
		else:
			row.append("0")
		row.append(getBinary(line[col.Necropsy]))
		row.append(getBinary(line[col.Metastasis]))
		row.append(line[col.Type])
		row.append(line[col.Location])
		row.append(getBinary(line[col.Primary]))
		row.append(col.Service)
		if col.Account:
			row.append(line[col.Account])
		else:
			row.append("NA")
		row.append(line[col.Submitter])
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
	serv = getService(infile)
	checkOutfile(outfile)
	with open(outfile, "a") as out:
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					spl = line.strip().split(d)
					res = formatLine(col, spl)
					if res:
						out.write(res + "\n")
				else:
					d = getDelim(line)
					col = Columns(line.split(d), serv)
					first = False

def main():
	parser = ArgumentParser(
"This script will assemble an upload file for the comparative oncology database.")
	parser.add_argument("-i", help = "Path to full record file.")
	parser.add_argument("-o", help = "Path to output csv (will append to existing file).")
	args = parser.parse_args()
	print(("\n\tSorting data from {}...\n").format(args.i))
	parseRecords(args.i, args.o)

if __name__ == "__main__":
	main()
