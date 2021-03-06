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
	numSubpeaks = int(tokens[7])
	parentArray = sorted(parentString.strip().replace(path,"").replace("_ext.tsv","").replace("/","").split("|"))
	size = int(tokens[3]) - int(tokens[2])
	peak = (id, stat, numSubpeaks, size)
	if len(parentArray)> 0:	
		key  = str(parentArray).replace("'","")
		if not key in groupHash:
			groupHash[key] = [peak]
		else:
			groupHash[key].append(peak)

# sort regions by size
groups = [(i , len(i.split(","))) for i in groupHash.keys()]
groups.sort(key = lambda x:x[1])

groupTotalPeaksHash = {k: len(groupHash[k])for k in groupHash.keys()} # key: group name, value: total number of merged region this group appears in, nonexclusive sense - merged regions are counted for multiple groups
for group1 in groups:
	# group is the larger group, group 2 is the smaller group
	group1set = set(group1[0][1:-1].split(", "))
	for group2 in groups:
		if not group1[0] == group2[0]:
			group2set = set(group2[0][1:-1].split(", "))
			if len(group1set & group2set) == len(group2set):
				groupTotalPeaksHash[group2[0]] += groupTotalPeaksHash[group1[0]]
		
_numInGroup = 0
_numPeaks = 0
_avgSubPeaks = 0
_avgStat = 0
_avgSize = 0
_totalPeaks = 0
print "### Stats Per Group ###"
print "Group\tNum Factors in Group\tNum Merged Peaks in Group\tTotal Merged Peaks\tAvg Num Subpeaks\tAvg Stat\tAvg Size"
for key in groupHash:
	avgSubPeaks = 0
	avgStat = 0
	avgSize = 0
	for peak in groupHash[key]:
		avgSubPeaks+=peak[2]
		avgStat += peak[1]
		avgSize += peak[3]
	numPeaks = len(groupHash[key])
	avgSubPeaks = float(avgSubPeaks)/float(numPeaks)
	avgStat = float(avgStat)/float(numPeaks)
	numInGroup = len(key.split(","))
	avgSize = float(avgSize)/float(numPeaks)
	totalPeaks = groupTotalPeaksHash[key]

	_numInGroup += numInGroup
	_numPeaks += numPeaks
	_avgSubPeaks += avgSubPeaks
	_avgStat += avgStat
	_avgSize += avgSize
	_totalPeaks += totalPeaks
	print key+"\t"+str(numInGroup)+"\t"+str(numPeaks)+"\t"+str(totalPeaks)+"\t"+str(avgSubPeaks)+"\t"+str(avgStat)+"\t"+str(avgSize)

print "### Overall Stats"
_numInGroup = float(_numInGroup)/float(len(groupHash.keys()))
_numPeaks = float(_numPeaks)/float(len(groupHash.keys()))
_avgSubPeaks = float(_avgSubPeaks)/float(len(groupHash.keys()))
_avgStat = float(_avgStat)/float(len(groupHash.keys()))
_avgSize = float(_avgSize)/float(len(groupHash.keys()))
print "total number of peaks\t"+str(len(data)-1)
print "number of groups:\t" + str(len(groupHash.keys()))
print "Num Factors in Group\tAvg Num Merged Peaks in Group\tAvg Total Peaks\tAvg Num Subpeaks\tAvg Stat\tAvg Size"
print str(_numInGroup)+"\t"+str(_numPeaks)+"\t"+str(_totalPeaks)+"\t"+str(_avgSubPeaks)+"\t"+str(_avgStat)+"\t"+str(_avgSize)

print "### PEAK ASSOCIATIONS ###"
for key in groupHash:
	toPrint = key+"\t"
	for peak in groupHash[key]:
		toPrint += peak[0]+"\t"
	print toPrint




		
	
