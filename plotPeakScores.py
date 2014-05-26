# given a path to a peak file, and an output file name, produces a plot showing the histogram of peak scores

### imports ###
import sys
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

# inputs: path to a peak file, output file path
# outputs: creates a histogram for the scores
def makePeakPlots(unfilteredPeakPath, filteredPeakPath, outPath):
	# read unfiltered peaks
	with open(unfilteredPeakPath) as f:
		data = f.readlines()
	start = 0 
	for line in data:
		if line[0] == "#":
			start += 1
	unfilteredTagCounts = []
	unfilteredPeakScores =[]
	for line in data[start:]:
		tokens = line.strip().split("\t")
		tagCount = float(tokens[5])
		peakScore = float(tokens[7])
		unfilteredTagCounts.append(tagCount)
		unfilteredPeakScores.append(peakScore)
	# read filtered peaks
	with open(filteredPeakPath) as f:
		data = f.readlines()
	start = 0 
	for line in data:
		if line[0] == "#":
			start += 1
	filteredTagCounts = []
	filteredPeakScores =[]
	for line in data[start:]:
		tokens = line.strip().split("\t")
		tagCount = float(tokens[5])
		peakScore = float(tokens[7])
		filteredTagCounts.append(tagCount)
		filteredPeakScores.append(peakScore)

	# plot peaks
	plt.hist(unfilteredTagCounts, filteredTagCounts, bins=100)
	ax = plt.gca()
	ax.legend(["Unfiltered", "Filtered"])
        plt.xlabel("Percentile")
        plt.ylabel("Frequency")
        plt.title("Tag Counts Frequency")
        plt.savefig(outPath+"_tagCount.png")
        plt.close()

	plt.hist(unfilteredPeakScores, fileredPeakScores, bins=100)
	ax = plt.gca()
	ax.legend(["Unfiltered", "Filtered"])
        plt.xlabel("Percentile")
        plt.ylabel("Frequency")
        plt.title("Peak Scores Frequency")
        plt.savefig(outPath+"_peakScore.png")
        plt.close()

if __name__ == "__main__":
	unfilteredPeakPath = sys.argv[1]
	filteredPeakPath = sys.argv[2]
	outPath = sys.argv[3]
	makePeakPlots(unfilteredPeakPath, filteredPeakPath, outPath)
