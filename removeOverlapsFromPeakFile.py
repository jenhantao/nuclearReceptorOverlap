# Given two paths to two peak files, remove peaks from the first file that appears in the second. prints new file to stdout
# inputs: paths to two peak files
# outputs: stdout

### imports ###
import sys

def filterPeakfile(path1, path2):
# read in data
	with open(path1) as f:
		data = f.readlines()
	start = 0
	for line in data:
		if line[0] == "#":
			print line.strip()
			start+=1
		else:  
			break
	peakLines1 = {} # key: chromosome, value: dictionary {position, line)
	for line in data[start:]:
		tokens = line.strip().split("\t")
		chrom = tokens[1]
		position = (int(tokens[2]), int(tokens[3]))
		if chrom in peakLines1:
			peakLines1[chrom][position] = line.strip()
		else:
			peakLines1[chrom] = {position:line.strip()}
			

	with open(path2) as f:
		data = f.readlines()
	start = 0
	for line in data:
		if line[0] == "#":
			start+=1
		else:  
			break
	peakLines2 = {}
	for line in data[start:]:
		tokens = line.strip().split("\t")
		chrom = tokens[1]
		position = (int(tokens[2]), int(tokens[3]))
		if chrom in peakLines2:
			peakLines2[chrom][position] = line.strip()
		else:
			peakLines2[chrom] = {position:line.strip()}


	for chromosome in peakLines1.keys():
		if chromosome in peakLines2:
			# sort peaks by start and end
			peakArray1 = sorted(peakLines1[chromosome].keys(), key = lambda x: (x[0],x[1]))
			peakArray2 = sorted(peakLines2[chromosome].keys(), key = lambda x: (x[0],x[1]))
			# check for overlaps
			for peak1 in peakArray1:
				seenSameChrom = False
				overlap = False
				for peak2 in peakArray2:
					if peak2[0] >= peak1[0] and peak2[0] <= peak1[1] or peak2[1] >=peak1[0] and peak2[1] <= peak1[0]:
						overlap = True
						break
				if not overlap:
					print peakLines1[chromosome][peak1]

				

			

if __name__ == "__main__":
	filterPeakfile(sys.argv[1], sys.argv[2])


