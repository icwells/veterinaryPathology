'''This script will combine the MSU pathology database files into one csv'''

import argparse
from datetime import datetime
from glob import glob
from string import digits
from sys import stdout
import os

def checkID(s):
	# Determines if element is an ID number
	total = 0
	if len(s) > 0:
		for i in s:
			if i in digits or i == ".":
				total += 1
		if total/len(s) >= 0.8:
			return True
	return False

def compileTSV(indir, outfile):
	# Compiles directory of csv files into one
	first = True
	row = []
	des = ""
	infiles = glob(indir + "*.tsv")
	length = len(infiles)
	print("\n\tJoining input files...")
	with open(outfile, "w") as output:
		for idx,i in enumerate(infiles):
			stdout.write(("\r\tReading {} of {} files...").format(idx+1, length))
			with open(i, "r") as f:
				for line in f:
					line = line.replace('"', '').strip()
					if first == False:
						if line:
							splt = line.split("\t")
							if checkID(splt[0]) == True and checkID(splt[1]) == True:
								if row:
									# Write existing output
									row.append(des)
									output.write("\t".join(row) + "\n")
									row = []
									des = ""
								row = splt
							elif splt[0] == "ID":
								# Skip remaining headers
								pass
							else:
								des += " " + line.replace("\t", " ")
					else:
						# Write header from first file
						output.write(line + "\tDescription\n")
						first = False

def main():
	starttime = datetime.now()
	parser = argparse.ArgumentParser(
description = "This script will combine the MSU pathology database files into one csv")
	parser.add_argument("-i", help = "Path to input directory.")
	parser.add_argument("-o", help = "Path to output csv.")
	args = parser.parse_args()
	if args.i[-1] != "/":
		args.i += "/"
	compileTSV(args.i, args.o)
	print(("\n\tFinished. Runtime: {}\n").format(datetime.now()-starttime))

if __name__ == "__main__":
	main()
