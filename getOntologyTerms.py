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
		groupNumber = directory.split("_")[1]
		directoryPath = join(path, path)
		toReturn[groupNumber] = (directoryPath+"biological_process.txt", directoryPath+"molecular_function.txt", directoryPath+"kegg.txt")
	return toReturn

# inputs: a path to ontology directories, and a mapping specifying which files correspond to which groups
# outputs: prints to stdout, a summary of the motif data
def getOntology(path, groupFileMapping, outPath):
	outFile = open(outPath, "w")
	
	


if __name__ == "__main__":
	inputPath = sys.argv[1]
	outPath = sys.argv[2]
	ontologyFiles = findDirectories(inputPath)
	getOntology(inputPath, ontologyFiles,outPath)
