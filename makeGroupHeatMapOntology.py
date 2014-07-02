# given a group summary file creates a heatmap showing the strength of each factors peak score in each merged region

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

# inputs: path to groups summary file, directory to place images in
# outputs: creates plot image file in in outPath
def plotScores(inputPath, outPath, mappingPath, toExclude = []):
	factorIndexDict = {}
	with open(mappingPath) as f:
		data = f.readlines()
	factors = []
	for line in data:
		tokens = line.strip().split("\t")
		factors.append(tokens[1])
	for te in toExclude:
		if te in factors:
			factors.remove(te)
	for i in range(len(factors)):
		factorIndexDict[factors[i]] = i

	# read in scores and bin according to chromosome
	with open(inputPath) as f:
		data = f.readlines()
	mergedRegions = []
	scoreMatrix = np.zeros((len(factors),len(factors)))
	for line in data[1:]:
		tokens = line.strip().split("\t")
		groupFactors = tokens[0].split()
		numSharedTerms = float(len(tokens)-1)
		for te in toExclude:
			if te in groupFactors:
				groupFactors.remove(te)
		# enumerate over all pairs in the group
		for i in range(len(groupFactors)-1):
			factor1 = groupFactors[i]
			ind1 = factorIndexDict[factor1]
			for j in range(i+1, len(groupFactors)):
				factor2 = groupFactors[j]
				ind2 = factorIndexDict[factor2]
				# each pair corresponds to two positions in the matrix
				scoreMatrix[ind1][ind2] += numSharedTerms
				scoreMatrix[ind2][ind1] += numSharedTerms
	# normalize each value as a fraction of the row factor
	rowTotals = scoreMatrix.sum(axis=1)
	for row in range(len(factors)):
		for column in range(len(factors)):
			scoreMatrix[row][column] = scoreMatrix[row][column]/rowTotals[row]
	# convert all values to log
	scoreMatrix = np.log(scoreMatrix)
	fig, ax = plt.subplots()
	img = ax.imshow(scoreMatrix, cmap=cm.Blues, interpolation="none") 
	fig.colorbar(img)
	plt.title("Ontology Term Co-occurrence Fraction")

	ax.set_yticks(np.arange(len(factors))+0.5, minor=False)
	ax.set_yticks(np.arange(len(factors)), minor=False)
        ax.set_yticklabels(factors, minor=False)		
	ax.set_xticks(np.arange(len(factors))+0.5, minor=False)
	ax.set_xticks(np.arange(len(factors)), minor=False)
        ax.set_xticklabels(factors, minor=False, rotation = 90)		

		
	# save files
	plt.savefig(outPath+"/groupHeatMapOntology.png", bbox_inches='tight', dpi=200)
	plt.close()
		
if __name__ == "__main__":
	summaryPath = sys.argv[1]
	outPath = sys.argv[2]
	mappingPath = sys.argv[3]
	plotScores(summaryPath, outPath, mappingPath)
	#plotScores(summaryPath, outPath, mappingPath, ["RXR","LXR","PU1"])
