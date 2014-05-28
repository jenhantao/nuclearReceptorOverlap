# given results from compareFilterThresholds.sh, produces a plot summarizing the number of peaks per factor at each threshold and the number of groups at each threshold; also accepts a mapping file to convert file names to factors

### imports ###
import sys 
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import numpy as np
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

# inputs: path to factor name mapping file
# output: a dictionary containing the mapping
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

# inputs: path to filter threshold results, output directory, and path to a mapping file
# outputs: creates plots as pngs in output directory
def plotFilterThresholdResults(resultsPath, outputPath, mapping):
	with open(resultsPath) as f:
		data = f.readlines()
	fileNames = data[-1].strip().split()
	thresholds = np.array(map(float,data[-2].strip().split()))
	groupCounts = np.array(map(float,data[-3].strip().split()))
	peakCounts = [[] for i in range(len(fileNames))]
	for line in data[:-3]:
		counts = np.array(map(float,line.strip().split()))
		for i in range(len(counts)):
			peakCounts[i].append(counts[i])
	# generate labels
	labels = []
	for i in range(len(fileNames)):
		file = fileNames[i]
		labels.append(mapping[file.split("-")[0]]+ "(max="+str(np.max(peakCounts[i]))+")")
	labels.append("merged regions (max="+str(np.max(groupCounts))+")")
	# normalize scores by largest value and then plot
	for i in range(len(peakCounts)):
		peakCounts[i] = np.array(peakCounts[i])
		peakCounts[i] = peakCounts[i]/np.max(peakCounts[i])
		plt.plot(thresholds, peakCounts[i], linewidth=2)
	# plot group counts
	groupCounts = groupCounts/np.max(groupCounts)
	plt.plot(thresholds, groupCounts, "o--", linewidth = 2)
	ax = plt.gca()
	# add title, labels and legend
	plt.title("Percentile Threshold vs Normalized Number of Peaks and Groups")
	plt.xlabel("Percentile Threshold")
	plt.ylabel("Normalized Number of Peaks/Groups")
	ax.legend(labels, loc=3, prop={"size":8})
	
	plt.savefig(outputPath+"/threshold_vs_groupsAndPeaks.png")



		




if __name__ == "__main__":
	resultsPath = sys.argv[1]
	outPath = sys.argv[2]
	mappingPath = sys.argv[3]
	mapping = readMapping(mappingPath)
	plotFilterThresholdResults(resultsPath, outPath, mapping)
