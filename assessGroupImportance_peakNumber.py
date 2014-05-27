# produces a graph visualization of a group stats file. 
# input: group stats file, output file path
# output: graph in DOT language format

### imports ###
import sys
import numpy as np
import math
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
		self.components = set()
		self.peaks = None
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
	groupNodeHash = {} # key: group name, value: node

	endIndex = len(groupArray)
	for i in range(len(groupArray)):
		parentName= groupArray[i][0]
		if not parentName in groupNodeHash:
			newNode = Node(parentName)
			newNode.components = groupComponentsHash[parentName]
			newNode.peaks = groupPeaksHash[parentName]
			groupNodeHash[parentName] = newNode
		parent = groupNodeHash[parentName]
		componentsToCover = parent.components.copy()
		slack = 1 # difference between the size of the parent an the size of the child
		for j in range(len(groupArray)):
			if not i==j:
				childName = groupArray[j][0]
				# create new nodes if necessary
				if not childName in groupNodeHash:
					newNode = Node(childName)
					newNode.components = groupComponentsHash[childName]
					newNode.peaks = groupPeaksHash[childName]
					groupNodeHash[childName] = newNode
				child = groupNodeHash[childName]
				if len(parent.components) == len(child.components)+slack:
					if len(parent.components & child.components) == len(child.components):
						componentsToCover = componentsToCover - child.components
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
	#generate graphviz file
	outFile = open(outputPath+"/hierarchy_peakZtest_"+str(threshold)+".txt","w")
	listFile = open(outputPath+"/hierarchy_peakZtest_"+str(threshold)+".tsv","w")

	outFile.write("graph {\n")
	outFile.write( "ratio=1.0\n")
	# create legend
	outFile.write( "{ rank = sink\n")
	outFile.write( "Legend[shape=none, margine=0, label =<\n")
	outFile.write( '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">\n')
	for factor in sorted(factorIndexHash.keys()):
		outFile.write( "<TR><TD>"+factor+"</TD><TD>"+factorIndexHash[factor]+"</TD></TR>\n")
	outFile.write( "</TABLE>>]\n")
	outFile.write( "}\n")

	queue = [root]
	seen = set()
	pairSet = set ()
	nameMappingDict = {} # key group name, value: converted name

	while queue:
		current = queue[0]
		queue = queue[1:]
		seen.add(current)
		for neighbor in current.neighbors:
			if not neighbor in seen and not (current,neighbor) in pairSet:
				queue.append(neighbor)
				node1=convertName(factorIndexHash, current.components, mapping)
				node2=convertName(factorIndexHash, neighbor.components, mapping)
				nameMappingDict[current.name] = node1
				nameMappingDict[neighbor.name] = node2

				outFile.write( '"'+ node1+ '" -- "'+node2+'"\n')
				pairSet.add((current,neighbor))
	# test each node and color accordingly
	vals = []
	for peakNumber in groupPeaksHash.values():
		x = float(peakNumber)
		vals.append(math.log(x))

	hist, bin_edges = np.histogram(vals)
	mean, se= fitNormal(vals,hist, bin_edges)
	
	listFile.write("Group\tp-value\tOutcome\n")
	for group in groupPeaksHash.keys():
		x = math.log(groupPeaksHash[group])
		z_score= (x-mean)/se
		p_val = norm.pdf(z_score)
		groupName= nameMappingDict[group]
		if p_val <= threshold:
			if z_score < 0.0:
				outFile.write( '"'+groupName + '" [fillcolor="red" style="filled" label="'+groupName+"|"+str(p_val)+'"]\n')
				listFile.write(groupName+"\t"+str(p_val)+"\t"+"down\n")
			else:
				outFile.write( '"'+groupName + '" [fillcolor="green" style="filled" label="'+groupName+"|"+str(p_val)+'"]\n')
				listFile.write(groupName+"\t"+str(p_val)+"\t"+"up\n")
		else:
			outFile.write( '"'+groupName + '" [label="'+groupName+"|"+str(p_val)+'"]\n')
			listFile.write(groupName+"\t"+str(p_val)+"\t"+"expected\n")
	outFile.write( "}\n")
	outFile.close()
	listFile.close()
	return root


# given an array of values, returns the mean and the standard deviation
def fitNormal(vals, hist, bin_edges):
	mean = np.mean(vals) 
	se = np.std(vals)/math.sqrt(len(vals))
	return mean,se


if __name__ == "__main__":
	groupStatsFilePath = sys.argv[1]
	mapping = None
	if len(sys.argv)>4:
		mapping = readMapping(sys.argv[4])
	threshold = float(sys.argv[2])
	outputPath = sys.argv[3]
	root = createGraph(groupStatsFilePath, outputPath, threshold, mapping)





