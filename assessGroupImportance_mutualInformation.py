# produces a graph visualization of a group stats file. 
# input: group stats file, output file path
# output: graph in DOT language format

### imports ###
import sys 
import math
import numpy as np
from scipy.stats import norm
	

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


class Node:
	def __init__(self, name = None):
		self.parent = None
		self.neighbors = []
		self.components = []
		self.peaks = None
		self.uniquePeaks = None
		self.name = name

def convertName(indexHash, components, factorMapping=None):
	compList = list(components)
	toReturn = []
	for comp in compList:
		toReturn.append(indexHash[comp])
		if mapping:
			toReturn[-1] = factorMapping[toReturn[-1]]
	return " ".join(toReturn)

def createGraph(groupStatsFilePath, outputPath, threshold, mapping = None):
	with open(groupStatsFilePath) as f:
		data = f.readlines()
	groupComponentsHash = {} # key: group name - individual factors count as groups, value: set of factors comprising that group
	factors = set()
	groupPeaksHash = {}
	groupPeaksUniqueHash = {}
	for line in data[2:]:
		if "###" in line:
			break
		tokens = line.strip().split("\t")
		group = tokens[0]
		groupPeaksHash[group] = int(tokens[3])
		groupPeaksUniqueHash[group] = int(tokens[2])
		groupTokens = group[1:-1].split(", ")
		groupComponentsHash[group] = groupTokens
		# add in individual factors
		for token in groupTokens:
			factors.add(token)
	factorIndexHash = {}
	counter = 1
	for factor in sorted(list(factors)):
		factorIndexHash[factor] = str(counter)
		counter += 1
	# sort groups according to number of components in group
	groupArray = [] 
	groupIndexHash = {}
	counter = 1
	for key in groupComponentsHash:
		groupArray.append((key,len(groupComponentsHash[key])))
		groupIndexHash[key] = str(counter)
		counter += 1
	groupArray.sort(key=lambda x: (x[1],x[0]))
	groupArray.reverse()
	groupIndexHash["Root"] = "Root"
	totalPeaks = 0
	for factor in factors:
		totalPeaks+=groupPeaksHash["["+factor+"]"]
	groupPeaksHash["Root"] = totalPeaks
	groupPeaksUniqueHash["Root"] = totalPeaks

	# create initial graph
	# create root node
	root = Node("Root")
	root.peaks = groupPeaksHash["Root"]
	root.uniquePeaks = groupPeaksUniqueHash["Root"]
	groupNodeHash = {} # key: group name, value: node
	for i in range(len(groupArray)):
                parentName= groupArray[i][0]
                if not parentName in groupNodeHash:
                        newNode = Node(parentName)
                        newNode.components = groupComponentsHash[parentName]
                        newNode.peaks = groupPeaksHash[parentName]
                        newNode.uniquePeaks = groupPeaksUniqueHash[parentName]
                        groupNodeHash[parentName] = newNode
                parent = groupNodeHash[parentName]
                componentsToCover = set(parent.components)
                slack = 1 # difference between the size of the parent an the size of the child
                for j in range(len(groupArray)):
                        if not i==j:
                                childName = groupArray[j][0]
                                # create new nodes if necessary
                                if not childName in groupNodeHash:
                                        newNode = Node(childName)
                                        newNode.components = groupComponentsHash[childName]
                                        newNode.peaks = groupPeaksHash[childName]
					newNode.uniquePeaks = groupPeaksUniqueHash[childName]
                                        groupNodeHash[childName] = newNode
                                child = groupNodeHash[childName]
                                if len(parent.components) == len(child.components)+slack:
                                        if len(set(parent.components) & set(child.components)) == len(child.components):
                                                componentsToCover = componentsToCover - set(child.components)
                                                child.parent = parent
                                                parent.neighbors.append(child)
                                elif len(parent.components) == len(child.components)+slack+1:
                                        if not componentsToCover:
                                                break
                                        else:
                                                slack += 1


	# attach nodes with no parents to the root
	for node in groupNodeHash.values():
		if node.parent == None and not node == root:
			node.parent = root
			root.neighbors.append(node)
		node.name = convertName(factorIndexHash, node.components, mapping)

	# gather the degree of overlap between each group
	queue = [root]
	seen = set()
	pairSet = set ()
	overlapSmallGroupFraction= [] #count of shared regions as a fraction of smaller group
	while queue:
		current = queue[0]
		queue = queue[1:]
		seen.add(current)
		for neighbor in current.neighbors:
			if not neighbor in seen and not (current,neighbor) in pairSet:
				overlapSmallGroupFraction.append(float(current.uniquePeaks)/float(neighbor.peaks))
				queue.append(neighbor)
				pairSet.add((current,neighbor))
	
	
	overlapSmallGroupFraction= np.log(np.array(overlapSmallGroupFraction))
	mean = np.mean(overlapSmallGroupFraction)
	sd = np.std(overlapSmallGroupFraction)
	se = sd/float(len(overlapSmallGroupFraction))
	# print graphviz file 
        outFile = open(outputPath+"/hierarchy_overlapZtest_"+str(threshold)+".txt","w")
        listFile = open(outputPath+"/hierarchy_overlapZtest_"+str(threshold)+".tsv","w")
        outFile.write("graph {\n")
        outFile.write( "ratio=1.0\n")
        outFile.write( "dpi=50\n")
	queue = [root]
	seen = set()
	pairSet = set ()
	while queue:
		current = queue[0]
		queue = queue[1:]
		seen.add(current)
		for neighbor in current.neighbors:
			if not neighbor in seen and not (current,neighbor) in pairSet:
				logOverlap = np.log(float(current.uniquePeaks)/float(neighbor.peaks))
				z_score = (logOverlap - mean)/se
				p_val = norm.pdf(z_score)	
				if p_val <= threshold:
					if z_score < 0.0:
						outFile.write('"'+current.name+'" -- "'+neighbor.name+'" [color="red" width=1.5]\n')
						listFile.write(current.name+"\t"+neighbor.name+"\t"+"up"+"\t"+str(p_val)+"\n")
					else:
						outFile.write('"'+current.name+'" -- "'+neighbor.name+'" [color="green" width=1.5]\n')
						listFile.write(current.name+"\t"+neighbor.name+"\t"+"down"+"\t"+str(p_val)+"\n")
				queue.append(neighbor)
				pairSet.add((current,neighbor))
	outFile.write("}")
	outFile.close()
	listFile.close()
	return root

if __name__ == "__main__":
	groupStatsFilePath = sys.argv[1]
	mapping = None
	if len(sys.argv)>4:
		mapping = readMapping(sys.argv[4])
	threshold = float(sys.argv[2])
	outputPath = sys.argv[3]
	root = createGraph(groupStatsFilePath, outputPath, threshold, mapping)





