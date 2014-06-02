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

# inputs: path to groups summary file, path to a peaks file, and base path for output files
# outputs: creates plot image file in in outPath
def plotScores(summaryPath, inputPath, outPath):
	with open(inputPath) as f:
		data = f.readlines()
	start = 0 
        for line in data:
                if line[0] == "#":
                        start += 1
	ids = set()
        for line in data[start:]:
                tokens = line.strip().split("\t")
		id = tokens[0]
		ids.add(id)
		
	with open(summaryPath) as f:
		data = f.readlines()
	factors = data[0].strip().split("\t")[4:]
	mergedRegions = []
	lineDict = {}
	otherIDs = set()
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
			if id in ids:
				mergedRegions.append((id,chromosome, start, end, peakScores))
	# sort by each factor and produce one heatmap for each
	for plotNumber  in range(len(factors)):
		mergedRegions = sorted(mergedRegions, key=lambda x: x[4][plotNumber])
		chromBreaks = [] # marks the breaks between chromosomes
		chromosomes = [] # chromosome labels
		scoreMatrix = np.zeros((len(factors),len(mergedRegions)))
		scoreArray = []
		sortedFile = open(outPath+"_sorted_summary_"+factors[plotNumber]+".tsv", "w")
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
		# remove zero columns
		toPlotFactors = []
		toPlotScores =[]
		for i in range(len(factors)):
			if np.sum(scoreMatrix[i]) > 0.0:
				toPlotFactors.append(factors[i])
				toPlotScores.append(scoreMatrix[i])
		toPlotScores = np.array(toPlotScores)


		fig, ax = plt.subplots()
		plt.pcolor(toPlotScores, cmap=cm.Blues)
		plt.colorbar()
			
		# fix ticks and labels
		ax.set_yticks(np.arange(len(toPlotFactors))+0.5, minor=False)
		ax.set_xticks(chromBreaks)
		ax.set_xticklabels([])
		ax.set_yticklabels(toPlotFactors, minor=False)
		plt.title("Log Peak Scores per Merged Region Per Factor")
		# save files
		plt.savefig(outPath+ "_positionHeatmap_"+factors[plotNumber]+".png", dpi=400)
		plt.close()
		sortedFile.close()
	
if __name__ == "__main__":
	summaryPath = sys.argv[1]
	inputPath = sys.argv[2]
	outPath = sys.argv[3]
	plotScores(summaryPath, inputPath, outPath)
	

	
