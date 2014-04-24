# produces a graph visualization of a group stats file. 
# input: group stats file
# output: graph in DOT language format

### imports ###
import sys

maxPenWidth = 10

groupStatsFilePath = sys.argv[1]

with open(groupStatsFilePath) as f:
	data = f.readlines()

groupPeaksHash = {} # key: group name, value: number of merged regions associated with peak
groupNameSet = set()
for line in data[2:]:
	if "###" in line:
		break
	tokens = line.strip().split("\t")
	group = tokens[0]
	groupPeaksHash[group] = float(tokens[2])
	

edgeHash = {} # key: tuple representing an edge, value: score associated with edge
for group in groupPeaksHash.keys():
	# add individual filenames to groupNameSet
	groupTokens = group[1:-1].split(", ")
	numPeaks = groupPeaksHash[group]
	for token in groupTokens:
		groupNameSet.add(token)
	# add an edge between each pair in the group
	for i in range(len(groupTokens)-1):
		for j in range(i+1, len(groupTokens)):
			tokenPairList = [groupTokens[i], groupTokens[j]]
			tokenPairList = sorted(tokenPairList)
			tokenPair = (tokenPairList[0], tokenPairList[1])
			if not tokenPair in edgeHash:
				edgeHash[tokenPair] = 1.0
			else:
				edgeHash[tokenPair] += 1.0
				
maxNumPeaks = max(groupPeaksHash.values())
maxEdgeScore = float(max(edgeHash.values()))


print "graph {"
for edge in edgeHash.keys():
	edgeScore = float(edgeHash[edge]/maxEdgeScore)
	edgeScore = edgeScore * float(maxPenWidth)
	edgeScore = int(max(1.0, edgeScore))
	if edgeScore > 1:
		print '"'+edge[0]+'" -- "'+edge[1]+'"' +'[penwidth="'+str(edgeScore)+'"]'
print "}"


	

