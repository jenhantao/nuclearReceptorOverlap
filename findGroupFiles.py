# given an input list of factors in numeric short hand, find the corresponding groups
# inputs: file path to list of queries, path to split peak files, factor index mapping files, group name file name mapping file
# outputs: prints to std out a tsv giving all relevant file paths to files

### imports ###
import sys

# given the paths to the 3 inputs described in the file header, return an array of tuples containing (query, peak file, bed file)
def findFilePaths(queryPath, filePath, factorMapping, fileMapping):
	# create group name to file mapping
	groupFileMapping = {} # key group name, value file name
	with open(fileMapping) as f:
		data = f.readlines()
	for line in data[1:]:
		tokens = line.strip().split("\t")
		groupTokens = sorted(tokens[0][1:-1].split(", "))
		groupFileMapping[str(groupTokens)] = tokens[1]
	
	# create factor index mapping
	indexFactorMapping = {} # key: index, value: factor with key index
	with open(factorMapping) as f:
		data = f.readlines()
	for line in data[1:]:
		tokens = line.strip().split("\t")
		indexFactorMapping[tokens[1]] = tokens[0]
		
	toReturn = []
	# convert numeric queries to sets of components
	with open(queryPath) as f:
		data = f.readlines()
	for query in data:
		tokens = query.strip().split()
		fullQuery = str(sorted([indexFactorMapping[x] for x in tokens]))
		peakFileName = groupFileMapping[fullQuery]
		bedFileName = peakFileName.replace("Peak","").replace("tsv","bed")
		toReturn.append((query.strip(),fullQuery.replace("'",""),filePath+"/"+peakFileName,filePath+"/"+bedFileName))
	return toReturn



if __name__ == "__main__":
	paths = findFilePaths(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	print "Query\tFull Query\tPeak file path\tBed file path"
	for result in paths:
		print "\t".join(result)
