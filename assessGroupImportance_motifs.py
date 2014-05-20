### imports ###
import sys


def readMotifInput(path):
	toReturn = {} #key group number, value: set of all motif sequences 
	with open(path) as f:
		data = f.readlines()
	for line in data[1:]:
		if "#" in line:
			break
		motifSet = set()
		tokens = line.strip().split("\t")
		groupNumber = tokens[0]
		for motif in tokens[1:]:
			sequence = motif[:motif.index(",")]
			motifSet.add(sequence)
		toReturn[groupNumber] = motifSet
	return toReturn

def buildGroupFactorMapping(groupFileMappingPath, factorNamePath):
	factorNameDict= {}
        with open(factorNamePath) as f:
                data = f.readlines()
        for line in data:
                tokens = line.strip().split("\t")
                factorNameDict[tokens[0]] = tokens[1]
	
	toReturn = {}
	with open(groupFileMappingPath) as f:
		data = f.readlines()
	for line in data[1:]:
		tokens = line.strip().split("\t")
		groupNumber = tokens[1].replace("groupPeaks_","").replace(".tsv","")
		componentTokens = tokens[0][1:-1].split(", ")
		name = " ".join([factorNameDict[x[:x.index("-")]] for x in componentTokens])
		toReturn[groupNumber] = name
	return toReturn
			

	



def buildGraph(motifSequenceDict, groupNameDict):
	groups = motifSequenceDict.keys()
	print "graph{"
	#print "ratio=1.0"
	noOverlap = set()
	for i in range(len(groups)-1):
		group1 = groups[i]
		group1sequences = motifSequenceDict[group1]
		for j in range(i+1, len(groups)):
			group2 = groups[j]
			group2sequences = motifSequenceDict[group2]
			overlap = len(group1sequences & group2sequences)
			if overlap > 0:
				print '"'+groupNameDict[group1] + '" -- "' + groupNameDict[group2] +'"'
			else:
				noOverlap.add(group1)
				noOverlap.add(group2)
	#for node in noOverlap:
		#print '"'+groupNameDict[node]+'"'
	print "}"


if __name__ == "__main__":
	motifStatsPath = sys.argv[1]
	groupSequenceDict = readMotifInput(motifStatsPath)
	groupFileMappingPath = sys.argv[2]
	factorNamePath = sys.argv[3]
	groupNameDict = buildGroupFactorMapping(groupFileMappingPath, factorNamePath)
	buildGraph(groupSequenceDict, groupNameDict)

