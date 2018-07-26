'''This script will assemble an upload file for the comparative oncology database'''

import os
from argparse import ArgumentParser
from vetPathUtils import *

def formatLine(col, line):
	# Return line formatted for writing to outfile
	row = []
	if len(line) >= col.Max:
		row.append(line[col.Sex])
		row.append(line[col.Age])
		# Castrated
		row.append(line[col.ID])
		row.append(line[col.Species])
		row.append(line[col.Date])
		row.append(line[col.Comments])
		# Masspresent
		# Metastatis
		row.append(line[col.Type])
		row.append(line[col.Location])
		# Primary
		row.append(col.Service)
		if col.Account >= 0:
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
			out.write("Sex,Age,Castrated,ID,Species,Date,Comments,MassPresent,\
Metastasis,TumorType,Location,Primary,Service,Account,Submitter\n")

def parseRecords(infile, outfile):
	# Sorts input and re-writes according to upload template
	first = True
	serv = getService(infile)
	with open(outfile, "w") as out:
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
	parseRecords(args.i, args.o)

if __name__ == "__main__":
	main()
