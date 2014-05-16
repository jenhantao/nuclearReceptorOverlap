# produces a graph visualization of a group stats file. 
# input: group stats file
# output: graph in DOT language format

### imports ###
import sys

class Node:
	def __init__(self, name = None):
		self.parent = None
		self.neighbors = []
		self.components = set()
		self.peaks = None
		self.name = name

def convertName(indexHash, components):
	compList = sorted(list(components))
	toReturn = []
	for comp in compList:
		toReturn.append(indexHash[comp])
	return " ".join(sorted(toReturn))

def createGraph(groupStatsFilePath, threshold):
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
	groupPeaksHash["Root"] = sum(groupPeaksHash.values())
	groupPeaksUniqueHash["Root"] = sum(groupPeaksHash.values())

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
	print "graph {"
	print "ratio=1.0"
	#print "dpi=50"
	# create legend
	print "{ rank = sink"
	print "Legend[shape=none, margine=0, label =<"
	print '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">'
	for factor in sorted(factorIndexHash.keys()):
		print "<TR><TD>"+factor+"</TD><TD>"+factorIndexHash[factor]+"</TD></TR>"
	print "</TABLE>>]"
	print "}"

	queue = [root]
	seen = set()
	pairSet = set ()
	nodes = set()

	while queue:
		current = queue[0]
		queue = queue[1:]
		seen.add(current)
		for neighbor in current.neighbors:
			if not neighbor in seen and not (current,neighbor) in pairSet:
				queue.append(neighbor)
				node1=convertName(factorIndexHash, current.components)+'|'+str(groupPeaksHash[current.name])+'|'+str(groupPeaksUniqueHash[current.name])
				node2=convertName(factorIndexHash, neighbor.components)+'|'+str(groupPeaksHash[neighbor.name])+'|'+str(groupPeaksUniqueHash[neighbor.name])
				print '"'+ node1+ '" -- "'+node2+'"'
				nodes.add(node1)
				nodes.add(node2)
				pairSet.add((current,neighbor))
	# test each node and color accordingly
	for node in nodes:
		x = float(node.split("|")[1])
		p_val = 0.9
		if p_val <= threshold:
			print '"'+node + '" [fillcolor="red" style="filled"]'
		else:
			print '"'+node + '"' 
	print "}"
	return root

# fits an exponential distribution to vals, returns the exponential distribution parameter lambda
def fitExponential(vals):
	toReturn = -1
	return toReturn

# given an array of values, returns the mean and the standard deviation
def fitNormal(vals):
	return np.mean(vals), np.std(vals)



if __name__ == "__main__":
	groupStatsFilePath = sys.argv[1]
	threshold = float(sys.argv[2])
	root = createGraph(groupStatsFilePath, threshold)





