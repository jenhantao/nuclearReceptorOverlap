# commands for running background test
inputPath=$1

# try Homer default
for path in $inputPath/groupPeaks_*.tsv
do
	command="findMotifsGenome.pl " 
	command+=" "$path 
	outPath=$path 
	outPath=${outPath%.tsv} 
	outPath=${outPath##*/}_default_motifs 
	command+=" mm9 ${inputPath}/${outPath}" 
	# create qsub file
	cp $inputPath/qsub_stub.sh qsub_script.sh
	echo $command >> $inputPath/qsub_script.sh
	qsub qsub_script.sh
	rm $inputPath/qsub_script.sh
	
done

# try suggested input
for path in $inputPath/groupPeaks_*.tsv
do
	if [ -f $inputPath/filteredInput.tsv ]
	then
		rm $inputPath/filteredInput.tsv
	fi
	groupNumber=$(basename $path)
	groupNumber=${groupNumber##groupPeaks_}
	groupNumber=${groupNumber%%.tsv}
	pythonCommand="python removeOverlapsFromPeakFile.py $inputPath/standardInputPeaks.tsv $path > $inputPath/filteredInput_${groupNumber}.tsv; "
	python removeOverlapsFromPeakFile.py $inputPath/standardInputPeaks.tsv $path > $inputPath/filteredInput_${groupNumber}.tsv
	command="findMotifsGenome.pl " 
	command+=" "$path 
	outPath=$path 
	outPath=${outPath%.tsv} 
	outPath=${outPath##*/}_suggestedInput_motifs
	command+=" mm9 ${inputPath}/${outPath}" 
	command+=" -bg $inputPath/filteredInput_${groupNumber}.tsv -size 200"
	findMotifsGenome.pl $path mm9 ${inputPath}/${outPath} -bg $inputPath/filteredInput_${groupNumber}.tsv -size 200
	# create qsub file
	cp $inputPath/qsub_stub.sh qsub_script.sh
	echo $pythonCommand >> qsub_script.sh
	echo $command >> qsub_script.sh
	qsub qsub_script.sh
	rm $inputPath/qsub_script.sh
	
done

