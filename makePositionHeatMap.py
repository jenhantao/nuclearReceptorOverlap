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

def plotScores(inputPath, outPath):
	with open(inputPath) as f:
		data = f.readlines()
	factors = data[0].strip().split("\t")[4:]
	# read in scores and bin according to chromosome
	mergedRegions = []
	for line in data[1:]:
		tokens = line.strip().split("\t")
		if not "random" in tokens[3]:
			peakScores = []
			for peakScore in tokens[4:]:
				if "," in peakScore:
					avgScore = np.sum(map(float,peakScore.split(",")))
					peakScores.append(avgScore)
				else:
					peakScores.append(float(peakScore))
			chromosome = tokens[3][3:tokens[3].index(":")]
			if chromosome.lower() == "x":
				chromosome = 20
			elif chromosome.lower() == "y":
				chromosome = 21
			elif chromosome.lower() == "mt":
				chromosome = 22
			else:
				chromosome = int(chromosome)
			start = int(tokens[3][tokens[3].index(":")+1:tokens[3].index("-")])
			end = int(tokens[3][tokens[3].index("-")+1:])
			mergedRegions.append((chromosome, start, end, peakScores))
	mergedRegions = sorted(mergedRegions, key=lambda x: (x[0], x[1]))
	chromBreaks = [] # marks the breaks between chromosomes
	x = []
	y = []
	z = []
	position = 0
	scoreMatrix = np.zeros((len(factors),len(mergedRegions)))
	for i in range(len(mergedRegions)):
		reg = mergedRegions[i]
		peakScores = reg[-1]
		for factorNumber in range(len(peakScores)):
			scoreMatrix[factorNumber][i] = peakScores[factorNumber]	
#			x.append(position)
#			y.append(factorNumber)
#			z.append(peakScores[factorNumber])
	fig, ax = plt.subplots()
	ax.set_aspect("equal")
	img = ax.pcolor(scoreMatrix, cmap=cm.gray)
	fig.colorbar(img)
	plt.savefig(outPath+"positionHeatMap.png")
	plt.close()
		

		
	# convert scores to x, y, and z coordinates
	scores = [[] for i in range(len(factors))]
	
	# plot a line indicating the boundary between chromosomes
	

if __name__ == "__main__":
	summaryPath = sys.argv[1]
	outPath = sys.argv[2]
	plotScores(summaryPath, outPath)
	

	
