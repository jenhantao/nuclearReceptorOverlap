# given a path to a DOT file created by assessGroupAssessment_peakNumber.py and assessGroupAssessment_mutualInformation.py, combines the two files. Taking nodes from the peak number assessment and edges from the mutual information assessment

### imports ###
import sys

def combineGraphs(peakNumberPath, mutualInformationPath):
	# read in edges
	with open(mutualInformationPath) as f:
		data = f.readlines()

	# read in nodes that appear in edges


if __name__ == "__main__":
	peakNumberPath = sys.argv[1]
	mutualInformationPath = sys.argv[2]
	combineGraphs(peakNumberPath, mutualInformationPath)
