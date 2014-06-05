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

nodeListPath = sys.argv[1]
edgeListPath = sys.argv[2]
outPath = sys.argv[3]

with open(nodeListPath) as f:
	data = f.readlines()
nodeStates = {} # key: node name: value: node state
nodeStates["Root"] = "expected"
for line in data[1:]:
	tokens = line.strip().split("\t")
	if len(tokens) > 2:
		nodeStates[tokens[0]] = tokens[2]


with open(edgeListPath) as f:
	data = f.readlines()
edgeStates = {} # key: node name: value: node state

listFile = open(outPath+"_networkSummary.tsv", "w")
listFile.write("node 1\tnode 2\tnode 1 status\tnode 2 status\tedge status\tnumber of shared terms\tterms\n")
edges = []
for line in data[1:]:
	tokens = line.strip().split("\t")
	node1 = tokens[0]
	node2 = tokens[1]
	status = tokens[2]
	sharedTerms = tokens[3]
	terms = ""
	if int(sharedTerms) > 0:
		terms = tokens[4]
	edges.append((node1,node2,status,sharedTerms))
	listFile.write("\t".join([node1,node2,nodeStates[node1],nodeStates[node2],status,sharedTerms,terms])+"\n")
listFile.close()

# plot edge and node type vs number of shared terms
numShared = {} # state type, number of shared
for edge in edges:
	stateType = (nodeStates[edge[0]], nodeStates[edge[1]], edge[2])
	shared = int(edge[3])
	if stateType in numShared:
		numShared[stateType] += shared
	else:
		numShared[stateType] = shared
y =[]
for stateType in sorted(numShared.keys()):
#	y.append(numShared[stateType])
	y.append(np.log(numShared[stateType]+1))
fig, ax = plt.subplots()
ax.bar(np.arange(len(y))+0.35, y, width=0.35)
ax = plt.gca()
ax.set_xticks(np.arange(len(y))+0.35)
ax.set_xticklabels(sorted(map(str,numShared.keys())))
labels = ax.get_xticklabels() 
for label in labels: 
    label.set_rotation(90) 
plt.xlabel("State Type (node1,node2,edge)")
plt.ylabel("Number of Shared Ontology Terms (log)")
plt.savefig(outPath+"_statesVsSharedTerms_log.png")
plt.close()

# plot edge type vs
numShared = {} # state type, number of shared
for edge in edges:
	stateType = nodeStates[edge[0]]
	shared = int(edge[3])
	if stateType in numShared:
		numShared[stateType] += shared
	else:
		numShared[stateType] = shared
y =[]
for stateType in  sorted(numShared.keys()):
	#y.append(numShared[stateType])
	y.append(np.log(numShared[stateType]+1))
fig, ax = plt.subplots()
ax.bar(np.arange(len(y))+0.35, y, width=0.35)
ax.set_xticks(np.arange(len(y))+0.35)
ax = plt.gca()
ax.set_xticklabels(sorted(map(str,numShared.keys())))
labels = ax.get_xticklabels() 
for label in labels: 
    label.set_rotation(90) 
plt.xlabel("State Type (edge)")
plt.ylabel("Number of Shared Ontology Terms (log)")
plt.savefig(outPath+"_edgeStatesVsSharedTerms_log.png")
plt.close()
	
	
# plot edge and node type vs number of shared terms
numShared = {} # state type, number of shared
for edge in edges:
	stateType = (nodeStates[edge[0]], nodeStates[edge[1]], edge[2])
	shared = int(edge[3])
	if stateType in numShared:
		numShared[stateType] += shared
	else:
		numShared[stateType] = shared
y =[]
for stateType in sorted(numShared.keys()):
	y.append(numShared[stateType])
fig, ax = plt.subplots()
ax.bar(np.arange(len(y))+0.35, y, width=0.35)
ax = plt.gca()
ax.set_xticks(np.arange(len(y))+0.35)
ax.set_xticklabels(sorted(map(str,numShared.keys())))
labels = ax.get_xticklabels() 
for label in labels: 
    label.set_rotation(90) 
plt.xlabel("State Type (node1,node2,edge)")
plt.ylabel("Number of Shared Ontology Terms (log)")
plt.savefig(outPath+"_statesVsSharedTerms.png")
plt.close()

# plot edge type vs
numShared = {} # state type, number of shared
for edge in edges:
	stateType = nodeStates[edge[0]]
	shared = int(edge[3])
	if stateType in numShared:
		numShared[stateType] += shared
	else:
		numShared[stateType] = shared
y =[]
for stateType in  sorted(numShared.keys()):
	y.append(numShared[stateType])
fig, ax = plt.subplots()
ax.bar(np.arange(len(y))+0.35, y, width=0.35)
ax.set_xticks(np.arange(len(y))+0.35)
ax = plt.gca()
ax.set_xticklabels(sorted(map(str,numShared.keys())))
labels = ax.get_xticklabels() 
for label in labels: 
    label.set_rotation(90) 
plt.xlabel("State Type (edge)")
plt.ylabel("Number of Shared Ontology Terms (log)")
plt.savefig(outPath+"_edgeStatesVsSharedTerms.png")
plt.close()
