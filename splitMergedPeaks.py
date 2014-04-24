# given a merged peak file and a group stats file, produce a peak file for each individual group. Due to file name naming contraints, each peak file for each group well be given an enumerated name. this script will also produce a text file giving the file name group name mapping

# inputs: path to merged peaks file, path to group stats file, output directory
# outputs: a bunch of peak files with enumerated names for each group, a text file giving the peak file name and group name mapping
import sys

peakFilePath = sys.argv[1]
statFilePath = sys.argv[2]
outputDirectory = sys.argv[3]

# read in peak lines and index with id
with open(peakFilePath) as f:
	data = f.readlines()
peakIdLineHash = {} # key: peak id, value: line in peak file corresponding to peak
for line in data[1:]:
	tokens = line.split("\t")
	id = tokens[0]
	peakIdLineHash[id] = line

# read in group stats file and get groups
with open(statFilePath) as f:
	data = f.readlines()
groupIDHash = {} # key: group name, value: array containing all peak ids
# get groups
startedAssociations = False
for i in range(len(data)):
	line = data[i]
	if not startedAssociations:
		if "PEAK ASSOCIATIONS" in line:
			startedAssociations = True
	else:
		print line
		tokens = line.strip().split("\t")
		groupIDHash[tokens[0]] = tokens[1:]

# write peak file for each group
groupFileNameHash = {} # key: group name, value: file name for the peak file for that group
count = 0
for group in sorted(groupIDHash.keys()):
	fileName = "groupPeaks_"+str(count)+".tsv"
	groupFileNameHash[group] = fileName
	count += 1
	outFile = open(outputDirectory+"/"+fileName,"w")
	outFile.write("Peak ID\tchr\tstart\tend\tStrand\tStat\n")
	for id in groupIDHash[group]:
		outFile.write(peakIdLineHash[id])
	outFile.close()

# write filename group mapping as a tsv
mappingFile = open(outputDirectory+"/groupPeakFileMapping.tsv","w")
mappingFile.write("Group Name\tPeak File Name\n")
for group in sorted(groupIDHash.keys()):
	mappingFile.write(group+"\t"+groupFileNameHash[group]+"\n")
mappingFile.close

	
