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
		self.level = -1
		self.name = name

def convertName(indexHash, components):
	compList = sorted(list(components))
	toReturn = []
	for comp in compList:
		toReturn.append(indexHash[comp])
	return " ".join(sorted(toReturn))

maxPenWidth = 10

groupStatsFilePath = sys.argv[1]

with open(groupStatsFilePath) as f:
	data = f.readlines()

groupComponentsHash = {} # key: group name - individual factors count as groups, value: set of factors comprising that group
factors = set()
groupPeaksHash = {}
for line in data[2:]:
	if "###" in line:
		break
	tokens = line.strip().split("\t")
	group = tokens[0]
	groupPeaksHash[group] = int(tokens[2])
	groupTokens = set(group[1:-1].split(", "))
	groupComponentsHash[group] = groupTokens
	# add in individual factors
	for token in groupTokens:
		#if not token in groupComponentsHash:
			#groupComponentsHash[token] = set([token])
			#groupPeaksHash[token] = 0 # fix this value later
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

# create initial graph
# create root node
root = Node("Root")
root.level = 0

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

for node in groupNodeHash.values():
	if node.parent == None and not node == root:
		node.parent = root
		root.neighbors.append(node)
## traverse graph and assign levels
nodeLevelHash = {0:[root]} # key: level, value: array of all nodes in that level
queue = [root]
while queue:
	current = queue[0]
	queue = queue[1:]
	if not current.parent == None:
		current.level = current.parent.level + 1
		if current.level in nodeLevelHash:
			nodeLevelHash[current.level].append(current)
		else:
			nodeLevelHash[current.level] = [current]
	for neighbor in current.neighbors:
		queue.append(neighbor)

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
while queue:
	current = queue[0]
	queue = queue[1:]
	seen.add(current)
	if not current.parent == None:
		current.level = current.parent.level + 1
	for neighbor in current.neighbors:
		if not neighbor in seen and not (current,neighbor) in pairSet:
			queue.append(neighbor)
			#print '"'+groupIndexHash[current.name]+'|'+str(len(current.components))+'|'+str(current.level)+'" -- "'+groupIndexHash[neighbor.name]+'|'+str(len(neighbor.components))+'|'+str(neighbor.level)+'"'
			#print '"'+convertName(factorIndexHash, current.components)+'|'+str(len(current.components))+'|'+str(current.level)+'" -- "'+convertName(factorIndexHash, neighbor.components)+'|'+str(len(neighbor.components))+'|'+str(neighbor.level)+'"'
			print '"'+convertName(factorIndexHash, current.components)+'|'+str(groupPeaksHash[current.name])+ '" -- "'+convertName(factorIndexHash, neighbor.components)+'|'+str(groupPeaksHash[neighbor.name])+'"'
			pairSet.add((current,neighbor))
			

print "}"


	

