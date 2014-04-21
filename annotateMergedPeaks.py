### imports ###
import sys
import operator
from os import listdir
from os.path import isfile, join

### classes ###

mergedPeakFilePath = sys.argv[1] # path to merged peak file
filePath = sys.argv[2] # path to annotated peak files
annotatedPeakFiles= [ f for f in listdir(filePath) if isfile(join(filePath,f)) and "annotated" in f]

filePeakHash = {} # key: chromosome, value: array of merged regions
'''
merged regions are expressed as a tuple with the following elements in this order
* chromosome
* start
* end
* strand
* receptor
'''
for file in annotatedPeakFiles:
	# read in peak file
	with open(filePath+file) as f:
		data=f.readlines()
	# read in each line as a peak
	'''
	peaks are expressed as a tuple with the following elements in this order
	chromosome
	start
	end
	strand
	'''
	peaks = []
	for line in data[1:]: # skip the first line, which is the column header
		tokens = line.strip().split()	
		peaks.append((tokens[1],int(tokens[2]),int(tokens[3]),tokens[4]))
	sortedPeaks = sorted(peaks,key=operator.itemgetter(0, 1, 2))
	filePeakHash[file] = sortedPeaks

print "finished reading peak files"
# read in merged file
idFilesHash = {} # key: merged peak id, value, array of files that appear in merged peak
with open(mergedPeakFilePath) as f:
	data = f.readlines()
peaks = []
for line in data[1:]: # skip the first line, which is the column header
	tokens = line.strip().split()	
	peaks.append((tokens[0], tokens[1],int(tokens[2]),int(tokens[3]),tokens[4]))
	idFilesHash[tokens[0]] = []
#sortedMergedPeaks = sorted(peaks,key=operator.itemgetter(1, 2, 3))
sortedMergedPeaks = peaks
print "finished reading merged peak file"

counter = 0
for mergedPeak in sortedMergedPeaks:
	print counter
	counter += 1
	mergedChrom = mergedPeak[1]
	mergedStart = mergedPeak[2]
	mergedEnd = mergedPeak[3]
	mergedId = mergedPeak[0]
	for file in filePeakHash.keys():
		for peak in filePeakHash[file]:
			peakChrom = peak[0]
			peakStart = peak[1]
			peakEnd = peak[3]
			if mergedChrom == peakChrom:
				if mergedStart <= peakStart and mergedEnd >= peakEnd: # if peak is within mergedPeak	
					idFilesHash[mergedId].append(file)






