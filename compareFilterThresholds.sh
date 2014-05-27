#! /bin/bash 

'''given paths to several nuclearReceptorOverlap outputs, creates a plot summarizing the number of merged regions per factor'''
thresholds=( 0 25 50 75 90 95 99 ) 

inputPath=$1
peaks=()
rm $outPath/filterCounts.txt
for i in "${thresholds[@]}"
do 
	currentValues=()
	peaks=()
	#overallCount=( $(wc -l $inputPath/test_actual_${i}/splitPeaks/groupPeakFileMapping.tsv) )
	overallCount=$(wc -l $inputPath/test_actual_${i}/splitPeaks/groupPeakFileMapping.tsv)
	overallCount=${overallCount%%[^0-9]*}
	echo "##### $i #####"
	echo $overallCount
	for path in $inputPath/test_actual_${i}/*_filteredPeaks.tsv
	do
		peaks+=($(basename $path))
		peakCount=$(wc -l $path)
		peakCount=${peakCount%%[^0-9]*}
		echo $peakCount
	done
done

echo "##### files #####"

#echo ${peaks[@]}
for file in ${peaks[@]}
do
	echo $file
done
