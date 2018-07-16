'''This script will extract/replace/remove lines from a file for given accounts.'''

import os
from argparse import ArgumentParser
from fuzzywuzzy import fuzz
from string import punctuation, digits
from re import sub

MIN = 0.95

def getDelim(line):
	# Returns delimiter
	for i in ["\t", ",", " "]:
		if i in line:
			return i
	print("\n\t[Error] Cannot determine delimeter. Check file formatting. Exiting.\n")
	quit()

def getTempFile(infile):
	# Returns tempfile name
	idx = infile.rfind(".")
	ext = infile[idx:]
	return infile[:idx] + ".tmp" + ext

def getAccountColumn(line, d):
	# Returns column index of account data
	spl = line.strip().split(d)
	for idx,i in enumerate(spl):
		if i == "Client" or i == "Owner":
			return idx
	print("\n\t[Error] Cannot find account column. Exiting.\n")
	quit()

#-----------------------------------------------------------------------------

def writeAccounts(outfile, accounts):
	# Write dict to file
	with open(outfile, "w") as out:
		out.write("OriginalName,CorrectedName\n")
		for t in accounts.keys():
			for j in accounts[t]:
				out.write(",".join([j,t]) + "\n")

def checkNA(term):
	# Check for nonsense values
	if term == "None":
		return "NA"
	if "Billing" in term or "Report" in term or "No " in term:
		return "NA"
	return term

def formatName(query):
	# Check query format
	# Replace multiple spaces
	term = sub(r" +", " ", query)
	for i in punctuation:
		if i != "." and i != "&":
			if i in term:
				term = term.replace(i, "")
	# Store in title case
	term = term.title()
	term = checkNA(term)
	if type(term) != str:
		term = "NA"
	elif term != "NA":
		if " Hosp" in term:
			idx = term.index(" Hosp")
			if idx + len(" Hosp") == len(term) or term[idx + len(" Hosp")] == " ":
				term = term.replace(" Hosp", " Hospital")
		elif " Anim" in term:
			term = term.replace(" Anim", " Animal")
		elif " A.C." in term or " A. C." in term:
			term = term.replace(" A.C.", " Animal Clinic").replace(" A. C.", " Animal Clinic")
		elif " A.H." in term or " A. H." in term:
			term = term.replace(" A.H.", " Animal Hospital").replace(" A. H.", " Animal Hospital")
		elif " V.C." in term or " V. C." in term:
			term = term.replace(" V.C.", " Veterinary Clinic").replace(" V. C.", " Veterinary Clinic")
		elif " V.H." in term or " V. H." in term:
			term = term.replace(" V.H.", " Veterinary Hospital").replace(" V. H.", " Veterinary Hospital")
		elif " V.S." in term or " V. S." in term:
			term = term.replace(" V.S.", " Veterinary Services").replace(" V. S.", " Veterinary Services")
	return term

def sortAccounts(acc):
	# Attempts to resolve misspellings and formatting errors
	accounts = {}
	for i in acc:
		term = formatName(i)
		if term in accounts:
			accounts[term].append(i)
		else:
			accounts[term] = [i]
	print(("\tIdentified {} formatted names {} total names.\n").format(len(accounts.keys()), len(acc)))
	return accounts

def extractAccounts(infile):
	# Extracts account names from input file
	first = True
	total = 0
	accounts = set()
	with open(infile, "r") as f:
		for line in f:
			if first == False:
				total += 1
				n = line.split(d)[c].strip()
				if len(n) >= 4:
					accounts.add(n)
			else:
				# Get info from header
				d = getDelim(line)
				c = getAccountColumn(line, d)
				first = False
	print(("\tExtracted {} unique names from {} entries.").format(len(accounts), total))
	return list(accounts)

#-----------------------------------------------------------------------------

def editLine(line, accounts, c, d):
	# Replaces account and returns line
	a = line[c].strip()
	if a in accounts.keys():
		line[c] = accounts[a]
	return d.join(line)

def checkAccount(line, accounts, c):
	# Returns false if line[c] is in accounts
	a = line[c].strip().lower()
	for i in accounts:
		if i in a:
			# Replace line
			return False
	return True

def replaceAccounts(infile, accounts, rm = False):
	# If rm == False, replaces account name with corrected name, else skips lines with account in accounts
	first = True
	total = 0
	removed = 0
	temp = getTempFile(infile)
	with open(temp, "w") as out:
		with open(infile, "r") as f:
			for line in f:
				if first == False:
					total += 1
					spl = line.split(d)
					if rm == False:
						line = editLine(spl, accounts, c, d)
					else:
						go = checkAccount(spl, accounts, c)
						if go == False:
							line = ""
					if line:
						out.write(line)
					else:
						removed += 1
				else:
					# Get info from header
					d = getDelim(line)
					c = getAccountColumn(line, d)
					out.write(line)
					first = False
	# Overwrite input file
	os.replace(temp, infile)
	if rm == True:
		print(("\tRemoved {} lines from {} total lines.\n").format(removed, total))

def getAccounts(a, rm = False):
	# Returns dict/list of accounts
	first = True
	if rm == True:
		accounts = []
		if not os.path.isfile(a):
			# Split and return list
			for i in a.split(","):
				accounts.append(i.lower)
			return accounts
	else:
		accounts = {}
	with open(a, "r") as f:
		# Read account names from text file
		for line in f:
			line = line.strip()
			if rm == False:
				# Get dict entry
				if first == True:
					d = getDelim(line)
					first = False
				spl = line.split(d)
				accounts[spl[0]] = spl[1]
			else:
				accounts.append(line.lower())
	return accounts

def checkArgs(args):
	# Identifies errors in arguments
	if not args.i:
		print("\n\t[Error] Please provide and input file. Exiting.\n")
		quit()
	if args.o and args.r or args.o and args.a or args.a and args.r:
		print("\n\t[Error] Please specify only one of: remove (-r), extract (-o), or replace (-a). Exiting.\n")
		quit()
	elif not args.o and not args.r and not args.a:
		print("\n\t[Error] Please specify one of: remove (-r), extract (-o), or replace (-a). Exiting.\n")
		quit()

def main():
	parser = ArgumentParser("This script will extract/replace/remove lines from a file for given accounts.")
	parser.add_argument("-r", help = "Accounts to be removed (either a text file or a comma seperated string).")
	parser.add_argument("-a", help = "Path to file containing corrected account names to replace existing names.")
	parser.add_argument("-i", help = "Path to input file.")
	parser.add_argument("-o", help = "Path to output file (provide to extract account names for manual curration).")
	args = parser.parse_args()
	checkArgs(args)
	if args.o:
		print(("\n\tExtracting accounts from {}").format(args.i))
		acc = extractAccounts(args.i)
		accounts = sortAccounts(acc)
		writeAccounts(args.o, accounts)
	elif args.a:
		print(("\n\tEditing accounts in {}").format(args.i))
		accounts = getAccounts(args.a)
		replaceAccounts(args.i, accounts)
	elif args.r:
		print(("\n\tRemoving accounts from {}").format(args.i))
		accounts = getAccounts(args.r, True)
		replaceAccounts(args.i, accounts, True)

if __name__ == "__main__":
	main()
