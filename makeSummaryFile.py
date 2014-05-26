# given a path to a group stats file, motif stats file, (optional) factor name mappings,  and all original factors peak files - create a human readable summary

### imports ###
import sys

# inputs: use file mapping, path to merged peaks, path to motif stats file, path 
def buildSummary(useFileMapping, mergedPath, groupStatsPath, motifStatsPath, factorPaths, factorMappingPath):
	factorNumberNameMapping = {}
	if useFileMapping:
		with open(factorMappingPath) as f:
			data = f.readlines()
		for line in data:
			tokens = line.strip().split("\t")
			factorNumberNameMapping[tokens[0]] = tokens[1]
			
	# read in individual peaks
	factorDict = {} # key factor file name, value: dictionary {peak id, tag count}
	for path in factorPaths:
		factor = path.split("/")[-1]
		if useFileMapping:
			factor = factorNumberNameMapping[path.split("/")[-1].split("-")[0]]
		factorDict[factor] = {}
		currentDict = factorDict[factor]
		with open(path) as f:
			data = f.readlines()
		start = 0
		for line in data:
			if line[0] == "#":
				start += 1
		for line in data[start:]:
			tokens = line.strip().split("\t")
			id = tokens[0]
			tagCount = tokens[5]
			peakScore = tokens[7]
			#currentDict[id] = tagCount
			currentDict[id] = peakScore
			
	# read in merged regions
	# for each merged, region, create a tuple that contains: the id, coordinates and a vector of which factors contributed to it
	mergedDict = {}
	with open(mergedPath) as f:
		data = f.readlines()
	factors = data[0].strip().split("\t")[8:]
	if useFileMapping:
		for i in range(len(factors)):
			factors[i] = factorNumberNameMapping[factors[i].split("/")[-1].split("-")[0]]
	for line in data[1:]:
		tokens = line.strip().split("\t")
		id = tokens[0]
		chr = tokens[1]
		start = tokens[2]
		end = tokens[3]
		peaks = tokens[8:]
		mergedDict[id] = (id, chr, start, end, peaks)
		
	# read in group stats file, get groups and merged regions
	associationDict = {}
	with open(groupStatsPath) as f:
		data = f.readlines()
	start = 1
	for line in data:
		if not "ASSOCIATIONS" in line:
			start += 1
		else:
			break
	for line in data[start:]:
		tokens = line.strip().split("\t")
		associationDict[tokens[0]] = tokens[1:]
		
	# do something with motifs

	# print file to standard out
	groupNumber = 0
	print "Group Number\tFactors\tID\tPosition\t"+"\t".join(factors)
	for group in sorted(associationDict.keys()):
		groupFactors= group[1:-1].split(", ")
		if useFileMapping:
			for i in range(len(groupFactors)):
				factor = factorNumberNameMapping[groupFactors[i].split("-")[0]]
				groupFactors[i] = factor
		for mergedID in associationDict[group]:
			mergedRegion = mergedDict[mergedID]
			position = mergedRegion[1]+":"+mergedRegion[2]+"-"+mergedRegion[3]
			peaks = mergedRegion[4]
			scores = []
			for i in range(len(peaks)):
				if not peaks[i] == "":
					if "," in peaks[i]:
						subScores = []
						peakTokens = peaks[i].split(",")
						for token in peakTokens:
							subScores.append(factorDict[factors[i]][token])
						scores.append(",".join(subScores))
					else:
						scores.append(factorDict[factors[i]][peaks[i]])
				else:
					scores.append("")
			print str(groupNumber)+"\t"+",".join(groupFactors)+"\t"+mergedID+"\t"+position+"\t"+"\t".join(scores)
		groupNumber += 1


if __name__ == "__main__":
	# read in inputs
	useFileMapping = bool(sys.argv[1])
	mergedPath = sys.argv[2]
	groupStatsPath = sys.argv[3]
	motifStatsPath = sys.argv[4]
	factorMappingPath = None
	factorPaths = sys.argv[5:]
	if groupStatsPath:
		factorMappingPath = sys.argv[-1]
		factorPaths = sys.argv[5:-1]
	buildSummary(useFileMapping, mergedPath, groupStatsPath, motifStatsPath, factorPaths, factorMappingPath)


