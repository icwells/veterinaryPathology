'''This script will extract/replace/remove lines from a file for given accounts.'''

import os
from datetime import datetime
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
		if i == "Client" or i == "Owner" or i == "Submitter":
			return idx
	print("\n\t[Error] Cannot find account column. Exiting.\n")
	quit()

#-----------------------------------------------------------------------------

def writeAccounts(outfile, accounts):
	# Write dict to file
	with open(outfile, "w") as out:
		out.write("OriginalName,CorrectedName\n")
		for i in accounts.keys():
			for j in accounts[i]:
				out.write(",".join([j,i]) + "\n")

def sortAccounts(accounts):
	# Uses fuzzy matching to resolve misspellings
	count = 1
	ret = {}
	keys = list(accounts.keys())
	for idx, k in enumerate(keys):
		if k != "NA":
			high = 0.0
			match = ""
			for i in keys[idx+1:]:
				score = fuzz.ratio(i, k)
				if score > high:
					high = score
					match = i
			if high >= 0.95:
				count += 1
				'''# Append lists
				if match in ret.keys():
					ret[match].extend(accounts[k])
				else:
					ret[k] = accounts[k].extend(accounts[match])
			else:
				# Store original list
				ret[k] = accounts[k]
		else:
			ret[k] = accounts[k]'''
	print(("\tFuzzy matching resolved {} formatted names to {} names.").format(len(accounts.keys()), count))
	return accounts

def checkAbbr(term):
	# Checks term for common abbreviations
	for i in ["Usa", "Wpz ", "Sw ", "Wsu ", " Vmc", "Dc", "Wa ", "La "]:
		if i in term:
			# Fix capitalization
			term = term.replace(i, i.upper())
	if "Univ" in term:
		idx = term.find("Univ") + len("Univ") + 1
		if idx >= len(term):
			term = term.replace("Univ", "University")
		elif term[idx] == ".":
			term = term.replace("Univ.", "University ")
		elif term[idx] == " ":
			term = term.replace("Univ ", "University ")
	if "Hosp" in term:
		idx = term.index("Hosp")
		if idx + len("Hosp") == len(term) or term[idx + len("Hosp")] == " ":
			term = term.replace("Hosp", "Hospital")
	if " Vet " in term:
		term = term.replace(" Vet ", " Veterinary ")
	elif term.find(" Vet") + len(" Vet") == len(term):
		term = term.replace(" Vet", " Veterinarian")
	for i in ["A.C.", "A. C.", "A.H.", "A. H.", "V.C.", "V. C.", "V.H.", "V. H.", 
			"V.S.", "V. S.", "P.V.", "P. V.", "Intl ", "Intl.", "Anim ", "Anim."]:
		# Check for variations of "Veterinary Hospital"
		if i in term:
			if i == "A.C." or i == "A. C.":
				rep = "Animal Clinic"
			elif i == "A.H." or i == "A. H.":
				rep =  "Animal Hospital"
			elif i == "V.C." or i == "V. C.":
				rep = "Veterinary Clinic"
			elif i == "V.H." or i == "V. H.":
				rep = "Veterinary Hospital"
			elif i == "V.S." or i == "V. S.":
				rep = "Veterinary Services"
			elif i == "P.V." or i == "P. V.":
				rep = "Pet Vet"
			elif i == "Intl " or i == "Intl.":
				rep = "International"
			elif i == "Anim " or i == "Anim.":
				rep = "Animal "
			term = term.replace(i, rep)
			break
	return term.strip()

def formatName(term):
	# Check query format
	if term.count("?") > 1:
		return "NA"
	for i in punctuation:
		if i != "." and i != "&" and i != "-" and i != "#" and i != "'":
			# Replace with a space and remove extra spaces later
			term = term.replace(i, " ")
	# Replace multiple spaces and put in title case
	term = sub(r" +", " ", term)
	term = term.strip().title()
	if term == "None" or "No " in term or "Not " in term:
		return "NA"
	term = checkAbbr(term)
	return term

def formatAccounts(acc):
	# Attempts to resolve capitalization and formatting errors
	accounts = {}
	for i in acc:
		term = formatName(i)
		if term in accounts:
			accounts[term].append(i)
		else:
			accounts[term] = [i]
	print(("\tIdentified {} formatted names from {} total names.").format(len(accounts.keys()), len(acc)))
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
	else:
		line[c] = "NA"
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
		print("\n\t[Error] Please provide an input file. Exiting.\n")
		quit()
	if args.o and args.r or args.o and args.a or args.a and args.r:
		print("\n\t[Error] Please specify only one of: remove (-r), extract (-o), or replace (-a). Exiting.\n")
		quit()
	elif not args.o and not args.r and not args.a:
		print("\n\t[Error] Please specify one of: remove (-r), extract (-o), or replace (-a). Exiting.\n")
		quit()

def main():
	start = datetime.now()
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
		accounts = formatAccounts(acc)
		#accounts = sortAccounts(accounts)
		writeAccounts(args.o, accounts)
	elif args.a:
		print(("\n\tEditing accounts in {}").format(args.i))
		accounts = getAccounts(args.a)
		replaceAccounts(args.i, accounts)
	elif args.r:
		print(("\n\tRemoving accounts from {}").format(args.i))
		accounts = getAccounts(args.r, True)
		replaceAccounts(args.i, accounts, True)
	print(("\tFinished. Runtime: {}\n").format(datetime.now()-start))

if __name__ == "__main__":
	main()
