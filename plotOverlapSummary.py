# produces a graph visualization of a group stats file. 
# input: group stats file, output file path
# output: graph in DOT language format

### imports ###
import sys 
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import numpy as np
from matplotlib import rcParams
import matplotlib.cm as cm
rcParams.update({'figure.autolayout': True})

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
		self.components = set()
		self.peaks = None
		self.uniquePeaks = None
		self.name = name

def convertName(indexHash, components, factorMapping=None):
	compList = sorted(list(components))
	toReturn = []
	for comp in compList:
		toReturn.append(indexHash[comp])
		if mapping:
			toReturn[-1] = factorMapping[toReturn[-1]]
	return " ".join(sorted(toReturn))

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
		groupTokens = set(group[1:-1].split(", "))
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

	endIndex = len(groupArray)
	for i in range(len(groupArray)):
		parentName= groupArray[i][0]
		if not parentName in groupNodeHash:
			newNode = Node(parentName)
			newNode.components = groupComponentsHash[parentName]
			newNode.peaks = groupPeaksHash[parentName]
			newNode.uniquePeaks = groupPeaksUniqueHash[parentName]
			groupNodeHash[parentName] = newNode
		parent = groupNodeHash[parentName]
		for j in range(len(groupArray)):
			if not i==j:
				childName = groupArray[j][0]
				# create new nodes if necessary
				if not childName in groupNodeHash:
					newNode = Node(childName)
					newNode.components = groupComponentsHash[childName]
					newNode.peaks = groupPeaksHash[childName]
					newNode.uniquePeaks= groupPeaksUniqueHash[childName]
					groupNodeHash[childName] = newNode
				child = groupNodeHash[childName]
				if len(parent.components & child.components) == len(child.components):
					child.parent = parent
					parent.neighbors.append(child)

	# attach nodes with no parents to the root
	for node in groupNodeHash.values():
		if node.parent == None and not node == root:
			node.parent = root
			root.neighbors.append(node)
		node.name = convertName(factorIndexHash, node.components, mapping)
	queue = [root]
	seen = set()
	pairSet = set ()

	# gather the degree of overlap between each group
	overlapCounts = [] #count of shared regions
	overlapLargeGroupFraction= [] #count of shared regions as a fraction of larger group
	overlapSmallGroupFraction= [] #count of shared regions as a fraction of smaller group
	while queue:
		current = queue[0]
		queue = queue[1:]
		seen.add(current)
		for neighbor in current.neighbors:
			if not neighbor in seen and not (current,neighbor) in pairSet:
				overlapCounts.append(current.uniquePeaks)
				overlapLargeGroupFraction.append(float(current.uniquePeaks)/float(current.peaks))
				overlapSmallGroupFraction.append(float(current.uniquePeaks)/float(neighbor.peaks))
				queue.append(neighbor)
				pairSet.add((current,neighbor))
	
	overlapCounts = np.array(overlapCounts)
	overlapLargeGroupFraction= np.array(overlapLargeGroupFraction)
	overlapSmallGroupFraction= np.array(overlapSmallGroupFraction)
	# plot distribution of scores on normal and log scale
	# normal scale plot
	plt.hist(overlapCounts, normed=True, bins=20)
	ax = plt.gca()
	ax.legend(["# Overlaps", "Large Group Fraction", "Small Group Fraction"])
	plt.ylabel("Frequency")
	plt.xlabel("Number of Overlaps")
	plt.title("Number of Overlapping Regions")
	plt.savefig(outputPath +"/mergedRegion_overlapCount.png")
	plt.close()

	plt.hist(overlapSmallGroupFraction, normed=True, bins=20)
	ax = plt.gca()
	ax.legend(["# Overlaps", "Large Group Fraction", "Small Group Fraction"])
	plt.ylabel("Frequency")
	plt.xlabel("Fraction")
	plt.title("Overlap as Fraction of Smaller Group")
	plt.savefig(outputPath +"/mergedRegion_smallGroupFraction.png")
	plt.close()

	plt.hist(overlapLargeGroupFraction, normed=True, bins=20)
	ax = plt.gca()
	ax.legend(["Large Group Fraction"])
	plt.ylabel("Frequency")
	plt.xlabel("Fraction")
	plt.title("Overlap as Fraction of Larger Group")
	plt.savefig(outputPath +"/mergedRegion_largeGroupFraction.png")
	plt.close()

	# log scale plot
	plt.hist(np.log(overlapCounts), normed=True, bins=20)
	ax = plt.gca()
	ax.legend(["# Overlaps", "Large Group Fraction", "Small Group Fraction"])
	plt.ylabel("Frequency")
	plt.xlabel("Number of Overlaps")
	plt.title("Number of Overlapping Regions")
	plt.savefig(outputPath +"/mergedRegion_overlapCount_log.png")
	plt.close()

	plt.hist(np.log(overlapSmallGroupFraction), normed=True, bins=20)
	ax = plt.gca()
	ax.legend(["# Overlaps", "Large Group Fraction", "Small Group Fraction"])
	plt.ylabel("Frequency")
	plt.xlabel("Fraction")
	plt.title("Overlap as Fraction of Smaller Group")
	plt.savefig(outputPath +"/mergedRegion_smallGroupFraction_log.png")
	plt.close()

	plt.hist(np.log(overlapLargeGroupFraction), normed=True, bins=20)
	ax = plt.gca()
	ax.legend(["Large Group Fraction"])
	plt.ylabel("Frequency")
	plt.xlabel("Fraction")
	plt.title("Overlap as Fraction of Larger Group")
	plt.savefig(outputPath +"/mergedRegion_largeGroupFraction_log.png")
	plt.close()

	return root

if __name__ == "__main__":
	groupStatsFilePath = sys.argv[1]
	mapping = None
	if len(sys.argv)>4:
		mapping = readMapping(sys.argv[4])
	threshold = float(sys.argv[2])
	outputPath = sys.argv[3]
	root = createGraph(groupStatsFilePath, outputPath, threshold, mapping)





