# given a directory containint motif results for default homer parameters and a dimethyl input file, creates a csv summary file
# inputs: path motif files

### imports ###
import sys
import os
import re
import numpy as np
import math
from os.path import isfile, join

# inputs: path to motif files
# outputs: a dictonary that links a group number with a tuple of file paths to motifs
def findDirectories(path):
	toReturn = {} # key: group number, tuple containing file paths for default motifs and motifs with inputs
	directories = [f for f in os.listdir(path) if not isfile(join(path,f))]
	directories.sort()
	for i in range(0,len(directories),2):
		if "motif" in directories[i]:
			defaultPath = directories[i]
			backgroundPath = directories[i+1]
			groupNumber = defaultPath.split("_")[1]
			#print groupNumber, defaultPath, backgroundPath
			toReturn[groupNumber] = (defaultPath, backgroundPath)
	return toReturn

# inputs: a path to motif directories, and a mapping specifying which files correspond to which groups
# outputs: prints to stdout, a summary of the motif data
def createMotifSummaryFile(path, groupFileMapping, outPath):
	motifFilePattern = re.compile("motif[0-9]+\.motif")
	statsDict = {} # key: group number, value: stats array with values in this order [targetFrac, backgroundFrac, p_val]
	outFile = open(outPath+"motifStats_default.tsv","w")
	outFile.write("### Group motifs ###\n")
	for key in sorted(groupFileMapping.keys()):
		# parse default motifs directory
		dir = path+groupFileMapping[key][0]+"/homerResults/"
		print dir
		statsDict[key] = [0.0,0.0,0.0]
		currentStats = statsDict[key]
		motifFiles = [f for f in os.listdir(dir) if isfile(join(dir,f)) and motifFilePattern.match(f)]
		toPrint = key
		for motif in motifFiles:
			with open(dir+motif) as f:
				idLine = f.readline()
			tokens =idLine.split("\t")
			sequence = tokens[0][1:]
			annotation = tokens[1][tokens[1].index(":")+1:]
			stats = tokens[5].split(",")
			targetFrac= float(stats[0][stats[0].index("(")+1:stats[0].index(")")-1])
			backgroundFrac= float(stats[1][stats[1].index("(")+1:stats[1].index(")")-1])
			p_val = float(stats[2][2:])
			statsDict[key][0] += targetFrac
			statsDict[key][1] += backgroundFrac
			statsDict[key][2] += p_val
			toPrint +="\t"+sequence+","+annotation+","+str(targetFrac)+","+str(backgroundFrac)+","+str(p_val)
		outFile.write(toPrint+"\n")
		numMotifs = len(motifFiles)
		currentStats = [float(x)/float(numMotifs) for x in currentStats]
		currentStats.append(numMotifs)
		statsDict[key] = currentStats
	outFile.write("### Group Stats ###\n")
	outFile.write("Group Number\tAverage Target Fraction\tAverage Background Fraction\tAverage p-value\tNumber of Motifs\n")
	for key in sorted(statsDict.keys()):
		outFile.write(key+"\t"+"\t".join(map(str,statsDict[key]))+"\n")
	outFile.close()

	statsDict = {} # key: group number, value: stats array with values in this order [targetFrac, backgroundFrac, p_val]
	outFile = open(outPath+"motifStats_standardInput.tsv","w")
	outFile.write("### Group motifs ###\n")
	for key in sorted(groupFileMapping.keys()):
		# parse background motifs directory
		dir = path+groupFileMapping[key][1]+"/homerResults/"
		print dir
		statsDict[key] = [[],[],[]]
		currentStats = statsDict[key]
		motifFiles = [f for f in os.listdir(dir) if isfile(join(dir,f)) and motifFilePattern.match(f)]
		toPrint = key
		for motif in motifFiles:
			with open(dir+motif) as f:
				idLine = f.readline()
			tokens =idLine.split("\t")
			sequence = tokens[0][1:]
			annotation = tokens[1][tokens[1].index(":")+1:]
			stats = tokens[5].split(",")
			targetFrac= float(stats[0][stats[0].index("(")+1:stats[0].index(")")-1])
			backgroundFrac= float(stats[1][stats[1].index("(")+1:stats[1].index(")")-1])
			p_val = float(stats[2][2:])
			statsDict[key][0].append(targetFrac)
			statsDict[key][1].append(backgroundFrac)
			statsDict[key][2].append(p_val)
			toPrint +="\t"+sequence+","+annotation+","+str(targetFrac)+","+str(backgroundFrac)+","+str(p_val)
		outFile.write(toPrint+"\n")
		numMotifs = len(motifFiles)
		meanStats= [math.fsum(x)/float(numMotifs) for x in currentStats]
		stdStats = [ np.std(x) for x in currentStats]
		finishedStats = meanStats+stdStats
		finishedStats.append(numMotifs)
		statsDict[key] = currentStats
	outFile.write("### Group Stats ###\n")
	outFile.write("Group Number\tstdev Target Fraction\tstdev Background Fraction\tstdev p-value\tstdev Target Fraction\tstdev Background Fraction\tstdev p-value\tNumber of Motifs\n")
	for key in sorted(statsDict.keys()):
		outFile.write(key+"\t"+"\t".join(map(str,statsDict[key]))+"\n")
	outFile.close()

	
	


if __name__ == "__main__":
	inputPath = sys.argv[1]
	outPath = sys.argv[2]
	# find pairs of motif directories
	filePairs = findDirectories(inputPath)
	createMotifSummaryFile(inputPath, filePairs,outPath)
