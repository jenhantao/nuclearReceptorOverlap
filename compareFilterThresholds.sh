#! /bin/bash 

thresholds=( 0 25 50 75 90 95 99 ) 

inputPath=$1
fileNames=()
mergedRegions=()

for i in "${thresholds[@]}"
do 
	currentValues=()
	fileNames=()
	overallCount=$(wc -l $inputPath/test_actual_${i}/splitPeaks/groupPeakFileMapping.tsv)
	overallCount=${overallCount%%[^0-9]*}
	mergedRegions+=($overallCount)
	for path in $inputPath/test_actual_${i}/*_filteredPeaks.tsv
	do
		fileNames+=($(basename $path))
		peakCount=$(wc -l $path)
		peakCount=${peakCount%%[^0-9]*}
		currentValues+=($peakCount)
	done
	echo ${currentValues[@]}
done

echo ${mergedRegions[@]}
echo ${fileNames[@]}
