# given an annotated peak file, produce a bed file that preserves all of the annotations
# inputs: path to peak file
# outputs: prints to std out a bed file

### imports ###
import sys

def convertPeakFile(inputPath):
	with open(inputPath) as f:
		data = f.readlines()
	for line in data[1:]:
		tokens = line.split("\t")
		id = tokens[0]
		chrom = tokens[1]
		start = tokens[2]
		end = tokens[3]
		strand = tokens[4]
		annotation = tokens[7]
		dist = tokens[9]
		nearestProm = tokens[10]	
		geneName = tokens[15]
		description = tokens[17]
		print "\t".join([chrom, start, end, id,"1",strand])
		print "\t".join([chrom, start, end, annotation,"1",strand]).replace(" ","_")
		print "\t".join([chrom, start, end, dist,"1",strand]).replace(" ","_")
		print "\t".join([chrom, start, end, nearestProm,"1",strand])
		print "\t".join([chrom, start, end, geneName,"1",strand])
		print "\t".join([chrom, start, end, description,"1",strand]).replace(" ","_")

if __name__ == "__main__":
	convertPeakFile(sys.argv[1])
