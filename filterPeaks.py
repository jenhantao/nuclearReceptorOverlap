# given a peaks file and a percentile threshold, prints to stdout all peaks with a tag count exceeding the threshold percentile

### imports ###
import sys
import math
import numpy as np

# inputs: path to a peak file, percentile threshold
def filterPeaks(peakFile, threshold):
	with open (peakFile) as f:
		data = f.readlines()
	start = 0 
	for line in data:
		if line[0] == "#":
			start += 1
	# read in scores
	scores = []	
	for i in range(start,len(data)):
		line = data[i]
		tokens = line.strip().split("\t")
		peakScore = float(tokens[7])
		scores.append(peakScore)
	thresholdScore = np.percentile(scores,threshold)
	for line in data[0:start]:
		print line.strip()
	
	for line in data[start:]:
		tokens = line.strip().split("\t")
		peakScore = float(tokens[7])
		if peakScore >= thresholdScore:
			print line.strip()

if __name__ == "__main__":
	peakFile = sys.argv[1]
	threshold = float(sys.argv[2])
	filterPeaks(peakFile, threshold)

	
