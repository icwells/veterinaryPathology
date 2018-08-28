'''This script will make a histogram of species occurances for each species in a given database.'''

from datetime import datetime
from argparse import ArgumentParser
from statistics import mode
import matplotlib.pyplot as plt
from unixpath import checkFile, getFileName
from vetPathUtils import *

def speciesHist(outfile, freq, title, mn):
	# Plots histogram of species occurances
	print("\tPlotting frequencies...")
	#ymax = getYMax(freq)
	# Plot frequencies on a log scale
	plt.hist(freq, int(len(freq)/10), facecolor = "b")
	'''plt.xscale('log', nonposx="clip")
	plt.yscale('log', nonposy="clip")
	# Add lines for 50 and 100
	plt.plot([50, 50], [0, 1000], color = "r", linewidth = 1)
	plt.plot([100, 100], [0, 1000], color = "r", linewidth = 1)'''
	# Add labels
	plt.title(title)
	plt.xlabel("Number of Records per Species")
	plt.ylabel("Frequency")
	txt = ("{} species contained\n>= {} entries.").format(len(freq), mn)
	plt.annotate(txt, xy = (0.80, 0.80), xycoords="axes fraction", ha="center", va="center")
	# Save as svg
	plt.savefig(outfile)	

def getSpeciesCounts(infile, mn):
	# Returns list of occurances for each species
	first = True
	sp = {}
	freq = []
	print("\n\tGetting species occurances...")
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				spl = line.split(d)
				if len(line) >= c.Max:
					# Only count complete lines
					s = spl[c.Species]
					if s not in sp.keys():
						sp[s] = 0
					sp[s] += 1					
			else:
				d = getDelim(line)
				c = Columns(line.split(d))
				first = False
	for i in sp.keys():
		if sp[i] >= mn:
			freq.append(sp[i])
	print(("\tIdentified {} species with at least {} entries.").format(len(freq), mn))
	return freq

def getTitle(infile, mn):
	# Returns formatted title name
	return ("Species Frequencies in {} (min >= {})").format(getFileName(infile), mn)

def main():
	start = datetime.now()
	parser = ArgumentParser("This script will make a histogram of species \
occurances for each species in a given database.")
	parser.add_argument("--min", type = int, default = 50,
 help = "The minimum number of records required for each species (default = 50).")
	parser.add_argument("infile", help = "Path to input file. Output svg will be written in same directory.")
	args = parser.parse_args()
	checkFile(args.infile)
	outfile = args.infile[:args.infile.rfind(".")] + ".svg"
	title = getTitle(args.infile, args.min)
	freq = getSpeciesCounts(args.infile, args.min)
	speciesHist(outfile, freq, title, args.min)
	printRuntime(start)

if __name__ == "__main__":
	main()
