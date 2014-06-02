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
import collections
import scipy
from scipy import stats

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
		#groupPeaksHash[group] = int(tokens[2]) 
		groupPeaksHash[group] = int(tokens[3]) # use total instead of peaks unique to the group
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

	# plot the log number of peaks per group/factor
	#plt.hist(groupPeaksHash.values())

	# fit a normal distribution
	sortedValues = sorted(map(math.log,groupPeaksHash.values()))
	fit = stats.norm.pdf(sortedValues, np.mean(sortedValues), np.std(sortedValues))
	plt.plot(sortedValues,fit,'-o')
	plt.hist(map(math.log, map(float,groupPeaksHash.values())),normed=True)
	plt.xlabel("Number of Peaks (ln)")
	plt.ylabel("Frequency")
	plt.title("All Factors/Groups VS Peaks")
	plt.savefig(outPath+"/allFactorsGroups_vs_mergedRegions_log.png")
	plt.close()

		
	# plot the number of peaks per group/factor
	from scipy import cluster
	sortedValues = sorted(groupPeaksHash.values())
	centroid = sorted(cluster.vq.kmeans(np.array(sortedValues), 3)[0])[1]
	std = np.std(sortedValues)
	mean = np.mean(sortedValues)
	sortedValues = [x for x in sortedValues if abs(x-centroid)<=std/2.0]
	# fit a poisson distribution
	param = np.mean(sortedValues)
	fit = stats.poisson.pmf(sortedValues, param)
	plt.plot(sortedValues,fit,'-o')
	plt.hist(sortedValues, normed=True, bins=10)

	plt.xlabel("Number of Peaks")
	plt.ylabel("Frequency")
	plt.title("All Factors/Groups VS Peaks")
	plt.savefig(outPath+"/allFactorsGroups_vs_mergedRegions.png")
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
	plt.savefig(outPath+"/factors_vs_groupOcurrence.png")
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
	plt.savefig(outPath+"/numFactors_vs_numPeaks.png")
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
	std_targetFracs = []
	std_backgroundFracs = []
	std_p_vals = []
	numMotifs = []
	groupNumbers = []

	for line in data[start:]:
		tokens = line.strip().split("\t")
		groupNumbers.append(tokens[0])
		targetFracs.append(float(tokens[1]))
		backgroundFracs.append(float(tokens[2]))
		p_vals.append(float(tokens[3]))
		std_targetFracs.append(float(tokens[4]))
		std_backgroundFracs.append(float(tokens[5]))
		std_p_vals.append(float(tokens[6]))
		numMotifs.append(int(tokens[7]))
		
	# plot the average target fractions per group
	plt.bar(range(len(targetFracs)),targetFracs)
	plt.hlines(float(math.fsum(targetFracs))/float(len(targetFracs)),0,len(targetFracs))
	plt.xlabel("Group")
	plt.ylabel("Target Fraction")
	plt.title("Average Motif Target Fraction per Group")
	plt.savefig(outputPath+"averageMotifTargetFraction.png")
	plt.close()
	

	# plot the average background fractions per group
	plt.bar(range(len(backgroundFracs)),backgroundFracs)
	plt.hlines(float(math.fsum(backgroundFracs))/float(len(backgroundFracs)),0, len(backgroundFracs))
	plt.xlabel("Group")
	plt.ylabel("Background Fraction")
	plt.title("Average Motif Background Fraction per Group")
	plt.savefig(outputPath+"averageMotifBackgroundFraction.png")
	plt.close()
	
	# plot the average p-value per group
	plt.bar(range(len(p_vals)),p_vals)
	plt.hlines(float(math.fsum(p_vals))/float(len(p_vals)),0, len(p_vals))
	plt.xlabel("Group")
	plt.ylabel("P-value")
	plt.title("Average Motif p-value per Group")
	plt.savefig(outputPath+"averageMotifPVals.png")
	plt.close()

	# plot the average number of motifs per group
	plt.bar(range(len(numMotifs)),numMotifs)
	plt.hlines(float(math.fsum(numMotifs))/float(len(numMotifs)),0, len(numMotifs))
	plt.xlabel("Group")
	plt.ylabel("Number of Motifs")
	plt.title("Average Number of Motifs per Group")
	plt.savefig(outputPath+"averageNumberofMotifs.png")
	plt.close()		

if __name__ == "__main__":
	createPeakSummaryPlots(sys.argv[1],sys.argv[2])
	#createMotifSummaryPlots(sys.argv[1],sys.argv[2])
	
