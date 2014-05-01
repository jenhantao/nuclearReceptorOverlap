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


maxPenWidth = 10

groupStatsFilePath = sys.argv[1]

with open(groupStatsFilePath) as f:
	data = f.readlines()

groupComponentsHash = {} # key: group name - individual factors count as groups, value: set of factors comprising that group
for line in data[2:]:
	if "###" in line:
		break
	tokens = line.strip().split("\t")
	group = tokens[0]
	groupTokens = set(group[1:-1].split(", "))
	groupComponentsHash[group] = groupTokens
	# add in individual factors
#	for token in groupTokens:
#		if not token in groupComponentsHash:
#			groupComponentsHash[token] = set([token])
# sort groups according to number of components in group
groupArray = [] 
groupIndexHash = {}
counter = 1
for key in groupComponentsHash:
	groupArray.append((key,len(groupComponentsHash[key])))
	groupIndexHash[key] = str(counter)
	counter += 1
groupArray.sort(key=lambda x: (x[1],x[0]))
groupIndexHash["Root"] = "Root"

# create initial graph
# create root node
root = Node("Root")
root.level = 1

groupNodeHash = {} # key: group name, value: node

endIndex = len(groupArray)
for i in range(len(groupArray)-1):
	for j in range(i+1, len(groupArray)):
		childName = groupArray[i][0]
		parentName = groupArray[j][0]
		# create new nodes if necessary
		if not childName in groupNodeHash:
			newNode = Node(childName)
			newNode.components = groupComponentsHash[childName]
			groupNodeHash[childName] = newNode
		child = groupNodeHash[childName]
		if not parentName in groupNodeHash:
			newNode = Node(parentName)
			newNode.components = groupComponentsHash[parentName]
			groupNodeHash[parentName] = newNode
		parent = groupNodeHash[parentName]
		if (len(parent.components & child.components) == len(child.components)):
			child.parent = parent
			parent.neighbors.append(child)
			break
		elif j == endIndex-1:
			root.neighbors.append(child)
			child.parent=root
# connect largest element to root
largest = groupNodeHash[groupArray[-1][0]]
root.neighbors.append(largest)
largest.parent = root

# traverse graph and assign levels
queue = [root]
while queue:
	current = queue[0]
	queue = queue[1:]
	if not current.parent == None:
		current.level = current.parent.level + 1
	for neighbor in current.neighbors:
		queue.append(neighbor)

# assign other edge types

#generate graphviz file
print "graph {"

queue = [root]
while queue:
	current = queue[0]
	queue = queue[1:]
	if not current.parent == None:
		current.level = current.parent.level + 1
	for neighbor in current.neighbors:
		print '"'+groupIndexHash[current.name]+'|'+str(len(current.components))+'" -- "'+groupIndexHash[neighbor.name]+'|'+str(len(neighbor.components))+'"'
		queue.append(neighbor)
			

print "}"


	
