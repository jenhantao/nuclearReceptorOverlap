# given a path to a DOT file created by assessGroupAssessment_peakNumber.py and assessGroupAssessment_mutualInformation.py, combines the two files. Taking nodes from the peak number assessment and edges from the mutual information assessment

### imports ###
import sys

def combineGraphs(peakNumberPath, mutualInformationPath, outPath):
	# read in edges
	with open(mutualInformationPath) as f:
		data = f.readlines()
	edgeLines = []
	nodeNames = set() # all nodes that appear in relevant edges
	for line in data:
		if "--" in line:
			edgeLines.append(line.strip())	
			tokens = line.split('"')
			nodeNames.add(tokens[1])
			nodeNames.add(tokens[3])
	
	# read in nodes that appear in edges
	with open(peakNumberPath) as f:
		data = f.readlines()
	nodeLines = []
	for line in data:
		if "fillcolor" in line:
			tokens = line.split(" [")
			nodeName = tokens[0][1:-1]
			if nodeName in line:
				nodeLines.append(line.strip())
	outFileUp = open(outPath+"_upRegulated.txt", "w")	
	outFileDown = open(outPath+"_downRegulated.txt", "w")	
	outFileUp.write("graph {\n")
	outFileUp.write("ratio=0.5\n")
	outFileDown.write("graph {\n")
	outFileDown.write("ratio=0.5\n")
	for node in nodeLines:
		outFileUp.write(node+"\n")
		outFileDown.write(node+"\n")
	for edge in edgeLines:
		if "green" in edge:
			outFileUp.write(edge+"\n")
		if "red" in edge:
			outFileDown.write(edge+"\n")

	outFileUp.write("}\n")
	outFileDown.write("}\n")


if __name__ == "__main__":
	peakNumberPath = sys.argv[1]
	mutualInformationPath = sys.argv[2]
	outPath = sys.argv[3]
	combineGraphs(peakNumberPath, mutualInformationPath, outPath)
