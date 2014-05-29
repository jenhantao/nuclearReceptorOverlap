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
	lineDict = {}
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
			id =tokens[2]
			lineDict[id] = line
			mergedRegions.append((id,chromosome, start, end, peakScores))
	# sort by chromosome and start
	mergedRegions = sorted(mergedRegions, key=lambda x: (x[1], x[2]))
	chromBreaks = [] # marks the breaks between chromosomes
	chromosomes = [] # chromosome labels
	position = 0
	scoreMatrix = np.zeros((len(factors),len(mergedRegions)))
	scoreArray = []
	sortedFile = open(outPath+"group_summary_sorted.tsv", "w")
	sortedFile.write(data[0])
	for i in range(len(mergedRegions)):
		reg = mergedRegions[i]
		peakScores = reg[-1]
		id = reg[0]
		chrom = reg[1]
		if not chrom in chromosomes:
			chromosomes.append(chrom)
			chromBreaks.append(i)
		sortedFile.write(lineDict[id])
		for factorNumber in range(len(peakScores)):
			if True:
				if peakScores[factorNumber] != 0.0:
					scoreMatrix[factorNumber][i] = math.log(peakScores[factorNumber])
					scoreArray.append(math.log(peakScores[factorNumber]))
				else:
					scoreMatrix[factorNumber][i] = peakScores[factorNumber]	
					scoreArray.append(peakScores[factorNumber])
			else:
				scoreMatrix[factorNumber][i] = peakScores[factorNumber]	
				scoreArray.append(peakScores[factorNumber])
	fig, ax = plt.subplots()
	img = ax.imshow(scoreMatrix, cmap=cm.Blues, extent=[0, len(mergedRegions),0,len(factors)],aspect =len(mergedRegions)/len(factors)/2, interpolation="none") 
	fig.colorbar(img)
	#plt.vlines(chromBreaks,len(factors),len(factors)+1, color="grey")
	# label chromosome breaks
#	for i in range(len(chromBreaks)-1):
#		chrBreak = chromBreaks[i]
#		chrBreakNext = chromBreaks[i+1]
#		plt.text((chrBreak+chrBreakNext)/2, len(factors)+0.5, chromosomes[i])
		
	# fix ticks and labels
	ax.set_yticks(np.arange(len(factors))+0.5, minor=False)
	ax.set_xticks(chromBreaks)
	ax.set_xticklabels([])
	factors.reverse()
	ax.set_yticklabels(factors, minor=False)
	plt.title("Peak Scores per Merged Region Per Factor")

	# save files
	plt.savefig(outPath+"positionHeatMap.png", bbox_inches='tight', dpi=400)
	#plt.show()
	plt.close()
	plt.hist(scoreArray, normed = True)
	plt.ylabel("frequency")
	plt.xlabel("score")
	plt.savefig(outPath+"positionHeatMap_peakScores.png")
	plt.close()
	sortedFile.close()
		

		
	# convert scores to x, y, and z coordinates
	scores = [[] for i in range(len(factors))]
	
	# plot a line indicating the boundary between chromosomes
	
if __name__ == "__main__":
	summaryPath = sys.argv[1]
	outPath = sys.argv[2]
	plotScores(summaryPath, outPath)
	

	
