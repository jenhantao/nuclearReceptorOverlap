### imports ###
import sys
import numpy
from os import listdir
from os.path import isfile, join

### classes ###

filePath = sys.argv[1]
peakFiles= [ f for f in listdir(filePath) if isfile(join(filePath,f)) and "annotated" in f]

mergedRegionHash = {} # key: chromosome, value: array of merged regions
'''
merged regions are expressed as a tuple with the following elements in this order
* chromosome
* start
* end
* strand
* receptor
'''
for file in peakFiles:
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
	# calculate overlaps in this file

### calculate overlaps ###

### print out results ###

# overlapping regions expressed as a peak file, a tsv with columns: unique peak id, chromosome, start, end, strand

