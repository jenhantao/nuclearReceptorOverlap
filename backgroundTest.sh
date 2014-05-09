# commands for running background test
source ~/nuclearReceptorOverlap/config.sh
inputPath=$1

# try Homer default
for path in $inputPath/*_peaks.tsv
do
	command="findMotifsGenome.pl " 
	command+=" "$path 
	outPath=$path 
	outPath=${outPath%_peaks.tsv} 
	outPath=${outPath##*/}_default_motifs 
	command+=" $genome ${inputPath}/${outPath}" 
	#echo $command 
	#$($command)
done

# try suggested input

for path in $inputPath/*_peaks.tsv
do
	if [ -f $inputPath/filteredInput.tsv ]
	then
		rm $inputPath/filteredInput.tsv
	fi
	python ~/nuclearReceptorOverlap/removeOverlapsFromPeakFile.py $inputPath/standardInputPeaks.tsv $path > $inputPath/filteredInput.tsv
	command="findMotifsGenome.pl " 
	command+=" "$path 
	outPath=$path 
	outPath=${outPath%_peaks.tsv} 
	outPath=${outPath##*/}_suggestedInput_motifs
	command+=" $genome ${inputPath}/${outPath}" 
	command+=" -bg $inputPath/filteredInput.tsv -size 200"
	echo $command 
	$($command)
done

# try paired input
for path in $inputPath/*_peaks.tsv
do	
	heading=$(basename $path)
	heading=${heading%%-*tsv}
	background=$(find $inputPath/inputPeaks/$heading* -maxdepth 0)
	command="findMotifsGenome.pl " 
	command+=" "$path 
	outPath=$path 
	outPath=${outPath%_peaks.tsv} 
	outPath=${outPath##*/}_pairedInput_motifs
	command+=" $genome ${inputPath}/${outPath}" 
	command+=" -bg $background"
	#echo $command 
	#$($command)
done

# iterate through each peak file and modify the start and the end
for path in $inputPath/*_peaks.tsv 
do 
	outPath=$path 
	outPath=${outPath%_peaks.tsv} 
	outPath=${outPath##*/}_ext.tsv 
	#python ~/nuclearReceptorOverlap/extendPeaks.py $path ${inputPath}/${outPath} $overlapDistance
done 

# merge all other peaks as background
for path in $inputPath/*_peaks.tsv
do
	if [ -f $inputPath/mergedBackground.tsv ]
	then
		rm $inputPath/mergedBackground.tsv
	fi
	# merge peaks
	command="mergePeaks -d given " 
	for path2 in $inputPath/*_peaks.tsv
	do
		if [ ! $path = $path2 ]
		then
			heading=${path2%%-*tsv}
			toMerge=$(find $heading*_ext.tsv -maxdepth 0)
			command+=" $toMerge"
		fi
	done
	#echo $command
	#$command > ${inputPath}/mergedBackground.tsv 
	# call motif analysis
	command="findMotifsGenome.pl " 
	command+=" "$path 
	outPath=$path 
	outPath=${outPath%_peaks.tsv} 
	outPath=${outPath##*/}_mergedInput_motifs
	command+=" $genome ${inputPath}/${outPath}" 
	command+=" -bg $inputPath/mergedBackground.tsv"
	#echo $command 
	#$($command)
done
