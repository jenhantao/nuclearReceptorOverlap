# given a group stats file, produce simple plots demonstrating the distribution of scores across all nodes
# inputs: group stats file, output file name
# outputs: plots visualizing the group stats

import sys
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

def createPeakSummaryPlots(inputPath,outPath):
	# read in inputs
        with open(inputPath) as f:
                data = f.readlines()

	factorFrequencyHash = {} # key - each factor; value: number of times each factor appears in a peak
	groupPeaksHash = {}# key - each group name, value: number of merged regions that appear in the peak
	groupComponentsHash = {}
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
			if token in factorFrequencyHash:
				factorFrequencyHash[token] += 1
			else:
				factorFrequencyHash[token] = 1	
		factorIndexHash = {}
		counter = 1
		for factor in sorted(list(factorFrequencyHash.keys())):
			factorIndexHash[factor] = str(counter)
			counter += 1

	# plot the number of peaks per group/factor
	plt.plot(sorted(groupPeaksHash.values(),reverse=True))
	plt.xlabel("Groups")
	plt.ylabel("Number of Peaks")
	plt.title("All Factors/Groups VS Peaks")
	plt.savefig(outPath+"allFactorsGroups_vs_mergedRegions.png")
	plt.close()

	# plot the number of merged regions per group
	filteredPeakValues = []
	for group in groupPeaksHash.keys():
		if len(groupComponentsHash[group]) > 1:
			filteredPeakValues.append(groupPeaksHash[group])
	plt.plot(sorted(filteredPeakValues,reverse=True))
	plt.xlabel("Groups")
	plt.ylabel("Number of Peaks")
	plt.title("Groups VS Peaks")
	plt.savefig(outPath+"groups_vs_mergedRegions.png")
	plt.close()
		
	# plot the number of times a factor appears in a group
	factorList = []
	for factor in factorFrequencyHash:
		factorList.append((factor, factorFrequencyHash[factor]))
	factorList.sort(key=lambda x: (x[1],x[0]))
	factorLabels = [x[0] for x in factorList]
	factorFrequencies = [x[1] for x in factorList]
	plt.bar(range(len(factorFrequencies)),factorFrequencies)
	plt.ylabel("Number of Groups")
	plt.xlabel("Factor")
	plt.xticks(range(len(factorLabels)), factorLabels, rotation=90,fontsize=8)
	plt.title("Factors vs Number of Ocurrences in a Group")
	plt.savefig(outPath+"factors_vs_groupOcurrence.png")
	plt.close()

	# plot the size of a group vs the number of merged regions
	groupList = []
	for group in groupPeaksHash:
		groupList.append((group, len(groupComponentsHash[group]), groupPeaksHash[group]))
	sizes = [x[1] for x in groupList]
	numPeaks = [x[2] for x in groupList]
	numPeaks = map(math.log,map(float,numPeaks))
	plt.scatter(sizes,numPeaks)
	plt.xlabel("Number of Factors in Group")
	plt.ylabel("Number of Peaks (ln)")
	plt.title("Number of Factors in Group VS Number of Peaks")
	plt.savefig(outPath+"numFactors_vs_numPeaks.png")
	plt.close()

def createMotifSummaryPlots(inputPath, outputPath):
	# read in input
        with open(inputPath) as f:
                data = f.readlines()

	factorFrequencyHash = {} # key - each factor; value: number of times each factor appears in a peak
	groupPeaksHash = {}# key - each group name, value: number of merged regions that appear in the peak
	groupComponentsHash = {}
	start = 3
	for line in data[1:]:
		if not "###" in line:
			start += 1
		else:
			break
	targetFracs = []
	backgroundFracs = []
	p_vals = []
	numMotifs = []
	groupNumbers = []

	for line in data[start:]:
		tokens = line.strip().split("\t")
		groupNumbers.append(tokens[0])
		targetFracs.append(float(tokens[1]))
		backgroundFracs.append(float(tokens[2]))
		p_vals.append(float(tokens[3]))
		numMotifs.append(int(tokens[4]))
		
		
	# plot the average target fractions per group
	plt.bar(range(len(targetFracs)),targetFracs)
	plt.xlabel("Group")
	plt.ylabel("Target Fraction")
	plt.title("Average Motif Target Fraction per Group")
	plt.savefig(outputPath+"averageMotifTargetFraction.png")
	plt.close()
	

	

if __name__ == "__main__":
	#createPeakSummaryPlots(sys.argv[1],sys.argv[2])
	createMotifSummaryPlots(sys.argv[1],sys.argv[2])
	
