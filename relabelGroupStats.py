
### imports ###
import sys
def readMapping(path):
        toReturn = {}
        with open(path) as f:
                data = f.readlines()
        for line in data:
                tokens = line.strip().split("\t")
                toReturn[tokens[0]] = tokens[1]
        if len(toReturn.keys()):
                return toReturn
        else:   
                return None

groupStatsPath = sys.argv[1]
mappingPath = sys.argv[2]

mapping = readMapping(mappingPath)

with open(groupStatsPath) as f:
	data = f.readlines()
for line in data:
	tokens = line.strip().split("\t")
	if "[" in tokens[0] and "]" in tokens[0]:
		# replace first column with mapped name
		nameTokens = tokens[0][1:-1].split(", ")
		factors = []
		for nt in nameTokens:
			factors.append(mapping[nt.split("-")[0]])
		tokens[0] = ",".join(factors)
	print "\t".join(tokens)
	
		
		
		
