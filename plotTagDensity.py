# given a path to a histogram file and a mapping file, plots the histogram

### imports ###
import sys 
import math
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import numpy as np
from matplotlib import rcParams
import matplotlib.cm as cm
rcParams.update({'figure.autolayout': True})

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
# inputs: path to histogram file from Homer, output file path, factor name mapping
def plotScores(inputPath, outPath, mapping):
	with open(inputPath) as f:
		data = f.readlines()
	headers = data[0].split("\t")[1::3]
	distances = []
	scores = [ [] for i in range(len(headers))]
	for line in data[1:]:
		tokens = line.strip().split("\t")
		distances.append(int(tokens[0]))
		scoreTokens = tokens[1::3]
		for i in range(len(scoreTokens)):
			scores[i].append(scoreTokens[i])
	for i in range(len(headers)):
		plt.plot(distances, scores[i])
	ax = plt.gca()
	# map headerto factor names
	factors = []
	for head in headers:
		factors.append(mapping[head.replace("\\","/").split("/")[-1].split("-")[0]])
	ax.legend(factors)
	plt.ylabel("ChIP Coverage (per bp per peak)")
	plt.xlabel("Distance from Peak Center")
	plt.savefig(outPath)
	plt.close()

if __name__ == "__main__":
	inputPath = sys.argv[1]
	outPath = sys.argv[2]
	mappingPath = sys.argv[3]
	mapping = readMapping(mappingPath)
	plotScores(inputPath, outPath, mapping)

