# given a path to a merged peaks file, computes stats for overlapping groups, printing the result out to standard out

### imports ###
import sys
import re

with open(sys.argv[1]) as f:
	data = f.readlines()

path = sys.argv[1][:-len(sys.argv[1].split("/")[-1])]
groupHash = {} # key: group id, value: array of tuples representing associated peaks
for line in data[1:]:
	tokens = line.strip().split("\t")
	id = tokens[0]
	stat = float(tokens[5])
	parentString = tokens[6]
	numPeaks = int(tokens[7])
	parentArray = parentString.strip().replace(path,"").replace("_ext.tsv","").split("|")
	peak = (id, stat, numPeaks)
	if len(parentArray)> 0:	
		key  = str(parentArray).replace("'","")
		if not key in groupHash:
			groupHash[key] = [peak]
		else:
			groupHash[key].append(peak)

#with open(sys.argv[2]) as f:
#	data = f.readlines()
#motifPattern = re.compile("^[+-]*[0-9]+\([ACTGactg]+.*\)")
#groupMotifCountHash = {} # key: group, value: number of motifs in group
#for line in data[1:]:
#	tokens = line.strip().split("\t")
#	id = tokens[0]
#	filteredTokens = [x for x in tokens if motifPattern.match(x)]
#	parentString = tokens[6]
#	parentArray = parentString.strip().replace(path,"").replace("_ext.tsv","").split("|")
#	key  = str(parentArray).replace("'","")

_numInGroup = 0
_numPeaks = 0
_avgSubPeaks = 0
_avgStat = 0
print "### Stats Per Group ###"
print "Group\tNum Factors in Group\tNum Merged Peaks in Group\tAvg Num Subpeaks\tAvg Stat"
for key in groupHash:
	avgSubPeaks = 0
	avgStat = 0
	for peak in groupHash[key]:
		avgSubPeaks+=peak[2]
		avgStat += peak[1]
	numPeaks = len(groupHash[key])
	avgSubPeaks = float(avgSubPeaks)/float(numPeaks)
	avgStat = float(avgStat)/float(numPeaks)
	numInGroup = len(key.split(","))

	_numInGroup += numInGroup
	_numPeaks += numPeaks
	_avgSubPeaks += avgSubPeaks
	_avgStat += avgStat
	print key+"\t"+str(numInGroup)+"\t"+str(numPeaks)+"\t"+str(avgSubPeaks)+"\t"+str(avgStat)

print "### Overall Stats"
_numInGroup = float(_numInGroup)/float(len(groupHash.keys()))
_numPeaks = float(_numPeaks)/float(len(groupHash.keys()))
_avgSubPeaks = float(_avgSubPeaks)/float(len(groupHash.keys()))
_avgStat = float(_avgStat)/float(len(groupHash.keys()))
print "total number of peaks\t"+str(len(data)-1)
print "number of groups:\t" + str(len(groupHash.keys()))
print "Num Factors in Group\tNum Merged Peaks in Group\tAvg Num Subpeaks\tAvg Stat"
print str(_numInGroup)+"\t"+str(_numPeaks)+"\t"+str(_avgSubPeaks)+"\t"+str(_avgStat)

print "### PEAK ASSOCIATIONS ###"
for key in groupHash:
	toPrint = key+"\t"
	for peak in groupHash[key]:
		toPrint += peak[0]+"\t"
	print toPrint




		
	
