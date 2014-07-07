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
def plotScores(inputPath, outPath, toExclude = []):
	with open(inputPath) as f:
		data = f.readlines()
	factors = data[0].strip().split("\t")[4:]
	for te in toExclude:
		if te in factors:
			factors.remove(te)
	factorIndexDict = {}
	for i in range(len(factors)):
		factorIndexDict[factors[i]] = i
	# read in scores and bin according to chromosome
	mergedRegions = []
	scoreMatrix = np.zeros((len(factors),len(factors)))
	for line in data[1:]:
		tokens = line.strip().split("\t")
		groupFactors = tokens[0].split(",")
		numSharedTerms =len(tokens[1])
		for te in toExclude:
			if te in groupFactors:
				groupFactors.remove(te)
		numShared = 
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
	img = ax.imshow(scoreMatrix, cmap=cm.Greens, interpolation="none") 
	fig.colorbar(img)
	plt.title("Peak  Co-occurrence Fraction")
	ax.set_yticks(np.arange(len(factors))+0.5, minor=False)
	ax.set_yticks(np.arange(len(factors)), minor=False)
        ax.set_yticklabels(factors, minor=False)		
	ax.set_xticks(np.arange(len(factors))+0.5, minor=False)
	ax.set_xticks(np.arange(len(factors)), minor=False)
        ax.set_xticklabels(factors, minor=False, rotation = 90)		

		
	# save files
	plt.savefig(outPath+"/groupHeatMapFraction.png", bbox_inches='tight', dpi=200)
	plt.close()
		
if __name__ == "__main__":
	summaryPath = sys.argv[1]
	outPath = sys.argv[2]
	plotScores(summaryPath, outPath)
