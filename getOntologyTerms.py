# given a directory containint motif results for default homer parameters and a dimethyl input file, creates a csv summary file
# inputs: path motif files

### imports ###
import sys
import os
import re
import numpy as np
import math
from os.path import isfile, join

# inputs: path to ontology files
# outputs: a dictonary that links a group number with a tuple of file paths to motifs
def findDirectories(path):
	toReturn = {} # key: group number, tuple containing file paths for gene ontology biological process and kegg analysis
	directories = [f for f in os.listdir(path) if not isfile(join(path,f))]
	for directory in directories:
		groupNumber = int(directory.split("_")[1])
		directoryPath = join(path, directory)
		toReturn[groupNumber] = (directoryPath+"/biological_process.txt", directoryPath+"/molecular_function.txt", directoryPath+"/kegg.txt")
	return toReturn

def getGroupMappings(groupMappingPath, factorNameMapping):
	numberFactorMapping = {}
	with open(factorNameMapping) as f:
		data = f.readlines()
	for line in data:
		tokens = line.strip().split("\t")
		numberFactorMapping[tokens[0]] = tokens[1]
	with open(groupMappingPath) as f:
		data = f.readlines()
	toReturn = {}
	for line in data[1:]:
		tokens = line.strip().split("\t")
		groupNumber = tokens[1][tokens[1].index("_")+1:tokens[1].index(".")]
		factors = []
		for token in tokens[0][1:-1].split(", "):
			factors.append(numberFactorMapping[token[:token.index("-")]])
			toReturn[groupNumber] = " ".join(factors)
	return toReturn
		
	

# inputs: a path to ontology directories, and a mapping specifying which files correspond to which groups
# outputs: prints to stdout, a summary of the motif data
def getOntology(path, groupFileMapping, significanceThreshold, outPath, mapping):
	logSig = np.log(significanceThreshold)
	outFile = open(outPath, "w")
	outFile.write("Group\tTerms\n")
	for group in sorted(groupFileMapping.keys()):
		toWrite = mapping[str(group)]
		files = groupFileMapping[group]
		biologicalFile = files[0]
		molecularFile = files[1]
		keggFile = files[2]
		# read biological process file
		with open(biologicalFile) as f:
			data = f.readlines()
		for line in data[1:]:
			tokens = line.strip().split("\t")
			term = tokens[1]
			logP = float(tokens[3])
			if logP <= logSig:
				toWrite += "\t"+term

		# read molecular function file
		with open(molecularFile) as f:
			data = f.readlines()
		for line in data[1:]:
			tokens = line.strip().split("\t")
			term = tokens[1]
			logP = float(tokens[3])
			if logP <= logSig:
				toWrite += "\t"+term

		# read kegg file
		with open(keggFile) as f:
			data = f.readlines()
		for line in data[1:]:
			tokens = line.strip().split("\t")
			term = tokens[1]
			logP = float(tokens[3])
			if logP <= logSig:
				toWrite += "\t"+term
		toWrite+="\n"
		outFile.write(toWrite)
	
	outFile.close()
	
	


if __name__ == "__main__":
	inputPath = sys.argv[1]
	significanceThreshold = float(sys.argv[2])*10 # relax a little bit
	outPath = sys.argv[3]
	groupMappingPath = sys.argv[4]
	factorNameMapping = sys.argv[5]
	ontologyFiles = findDirectories(inputPath)
	mapping = getGroupMappings(groupMappingPath, factorNameMapping)	
	getOntology(inputPath, ontologyFiles,significanceThreshold, outPath, mapping)
