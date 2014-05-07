import sys

input = sys.argv[1]
output = sys.argv[2]
overlapDistance = int(sys.argv[3])

with open(input) as f:
	data = f.readlines()
outputFile = open(output,'w')
outputFile.write(data[0])
start = 0
for line in data:
	if line[0] == "#":
		start+=1
	else:
		break
for line in data[start:]:
	tokens = line.split("\t")
	start = int(tokens[2])
	end = int(tokens[3])
	if start >= overlapDistance:
		start -= overlapDistance
	else:
		start = 0

	end += overlapDistance
	tokens[2] = str(start)
	tokens[3] = str(end)
	outputFile.write("\t".join(tokens))
outputFile.close()
