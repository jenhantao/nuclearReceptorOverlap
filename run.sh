#! /bin/bash

# runs the analysis pipeline
source config.sh

# define input variables
inputPath=$1 # path to directory containing all tag directories
outputDir=$2 # path to the output directory
stepOne=$3 # run basic analysis for each tag directory
stepTwo=$4 # mege peaks and look for overlapping cistromes
stepThree=$5 # conduct differential motif analysis on overlapping cistromes

### FOR THRESHOLD GRADIENT ###
percentileThreshold=$6

if [ ! -d $outputDir ]
then
mkdir $outputDir
fi
# create a file summarizing the parameters used
cp config.sh $outputDir/runParams.txt
echo "inputPath=$1" >>$outputDir/runParams.txt
echo "outputDir=$2" >>$outputDir/runParams.txt
echo "stepOne=$3" >>$outputDir/runParams.txt
echo "stepTwo=$4" >>$outputDir/runParams.txt
echo "stepThree=$5" >>$outputDir/runParams.txt
echo "percentileThreshold=$6" >> $outputDir/runParams.txt
echo "hub url = http://glassome.ucsd.edu/hubs/$(basename $outputDir)/hub.txt" >>$outputDir/runParams.txt

### basic analysis for each the peaks and define cistromes ###
if $stepOne
then
	# validation and update if necessary
	for path in $inputPath/*
	do
		[ -e "${path}/tagInfo.txt" ] || continue # if not a directory, skip
		# if mm9 is specified, it should appear in tagInfo.txt at least once
		mm9=$(grep $genome $path/tagInfo.txt | wc -l)
		if [ "$mm9" == "0" ]
		then
			echo "WARNING: the following tag directory does not use the genome ${genome}: $path"
		fi
		# update tag directories if option is on
		if $updateTags
		then
			command="makeTagDirectory ${path} -update -genome mm9"
			echo $command
			$($command)
		fi
	done

	#UCSC visualization (makeUCSCfile, makeBigWig.pl)
	if $makeUCSC
	then
		echo "making UCSC multibig wig file"
		# iterate over all tag directories and make a hub	
		hub=$(basename $outputDir)
		command="makeMultiWigHub.pl $hub $genome -force -d"
		for path in $inputPath/*
		do
   			[ -d "${path}" ] || continue # if not a directory, skip
			# skip directories that contain input
			if [[ ! $path  =~ .*[iI]{1}nput.* ]]
			then
				if [[ $(basename $path) =~ ^[0-9]-.* ]]
				then
					command+=" "
					# append tag directory to command
					command+="$path"
				fi
			fi
		done
		echo "$command"
		$($command)
	
	fi
	#Peak finding / Transcript detection / Feature identification (findPeaks)
	if $findPeaks 
	then
		echo "finding peaks"
		rm -rf $outputDir/inputPeaks
		mkdir $outputDir/inputPeaks
	
		fileHeadings=()
		for path in $inputPath/*
		do
			[ -d "${path}" ] || continue # if not a directory, skip
			basepath=$(basename $path)
			if [[ $basepath =~ ^[0-9]-.* ]]; 
			then
				fileHeadings+=(${basepath%%-*})
			fi          
		done
		# get the list of unique headings
		uniqueHeadings=($(for v in "${fileHeadings[@]}"; do echo "$v";done| sort| uniq| xargs))
		for heading in ${uniqueHeadings[@]}
		do
			files=( $(find $inputPath/$heading* -maxdepth 0) )
			control=''
			actual=''
			if [[ ${files[0]} =~ .*[iI]{1}nput.* ]]
			then
				control=${files[0]}
				actual=${files[1]}
			else
				control=${files[1]}
				actual=${files[0]}
			fi  
				command="findPeaks "
				command+=" "$actual
				command+=" -style factor -o $outputDir/$(basename ${actual})_peaks.tsv"
				if $useControl
				then
					command+=" -i $control"
				fi
				echo $command
				$($command)
				inputCommand="findPeaks $control -style factor -o $outputDir/inputPeaks/$(basename ${control})_peaks.tsv"
				echo $inputCommand
				$($inputCommand)
		done
	fi

	echo "filtering peaks"
	# filter peaks summarize peak score and tag counts of each file
	for path in $outputDir/*_peaks.tsv
	do
		[ -f "${path}" ] || continue
		filteredPath=${path%_peaks.tsv}
		filteredPath+="_filteredPeaks.tsv"
		echo "python filterPeaks.py $path > $filteredPath"
		python filterPeaks.py $path $percentileThreshold > $filteredPath
		outpath=${path%_peaks.tsv}
		echo "python plotPeakScores.py $path $filteredPath $outpath"
		python plotPeakScores.py $path $filteredPath $outpath
	done
	if [ -d $outputDir/peakScorePlots ]
	then
	rm -rf $outputDir/peakScorePlots
	fi
	mkdir $outputDir/peakScorePlots
	mv $outputDir/*_peakScore.png $outputDir/peakScorePlots
	mv $outputDir/*_tagCount.png $outputDir/peakScorePlots
	# create bed files for each peak file
	for path in $outputDir/*_filteredPeaks.tsv
	do
		outPath=$(basename $path)
		outPath=${outPath%%_filteredPeaks.tsv}
		outPath+=".bed"
		echo "pos2bed.pl $path > $outputDir/$outPath"
		pos2bed.pl $path > $outputDir/$outPath
	done

	#Motif analysis (findMotifsGenome.pl)
	if $findMotifs
	then
		echo "finding motifs"
		mkdir $outputDir/factorMotifs
		for path in $outputDir/*_filteredPeaks.tsv
		do
   			[ -f "${path}" ] || continue
			command="findMotifsGenome.pl "
			command+=" "$path
			# run commands in the background
			outPath=$path
			outPath=${outPath%_filteredPeaks.tsv}
			outPath=${outPath##*/}_motifs
			command+=" $genome ${outputDir}/factorMotifs/${outPath}"
			echo $command
			$($command)
		done

	fi
	#Annotation of Peaks (annotatePeaks.pl)
	if $annotatePeaks
		then
			echo "annotating peaks"
			for path in $outputDir/*_filteredPeaks.tsv
			do
				[ -f "${path}" ] || continue
				command="annotatePeaks.pl"
				command+=" "$path
				# run commands in the background
				outPath=$path
				outPath=${outPath%_filteredPeaks.tsv}
				outPath=${outPath##*/}_annotatedPeaks.tsv
				#command+=" $genome > ${outputDir}/${outPath}"
				command+=" $genome"
				echo $command
				$($command > ${outputDir}/${outPath})
			done
			# annotate merged regions with all tag directories and all motifs
			command="annotatePeaks.pl $outputDir/merged.tsv mm9 -size 200 -d"
			for path in $inputPath/*
			do
				[ -d "${path}" ] || continue # if not a directory, skip
				# skip directories that contain input
				if [[ ! $path  =~ .*[iI]{1}nput.* ]]
				then
					# consider only files tagged with a number at the front
					if [[ $(basename $path) =~ ^[0-9]-.* ]]
					then
						command+=" "
						# append tag directory to command
						command+="$path"
					fi
				fi
		done
		if $findMotifs
		then
			command+=" -m $outputDir/mergedMotifs/homerMotifs.all.motifs"
		fi
		echo $command
		$command > $outputDir/merged_annotated.tsv
	fi
	#Quantification of Data at Peaks/Regions in the Genome/Histograms and Heatmaps (annotatePeaks.pl)
	if $quantifyPeaks 
	then
		echo "quantifying peaks"
		# not sure what I need to do here, this will evolve later on
		# the same script is used for annotating peaks, and so this can be wrapped in the previous section
	fi
fi

### merge the peaks and look for overlapping cistromes ##
if $stepTwo
then
	echo "calculating overlapping cistromes"

	echo "extending peaks"
	# iterate through each peak file and modify the start and the end
	for path in $outputDir/*_filteredPeaks.tsv
	do
		[ -f "${path}" ] || continue
		outPath=$path
		outPath=${outPath%_filteredPeaks.tsv}
		outPath=${outPath##*/}_ext.tsv
		echo "python extendPeaks.py $path ${outputDir}/${outPath} $overlapDistance"
		python extendPeaks.py $path ${outputDir}/${outPath} $overlapDistance
	done
	# call merge peaks
	# remove merged_ext.tsv just in case
	if [-f $outputDir/merged_ext.tsv ]
	then
		rm $ouptputDir/merged_ext.tsv
	fi
	command="mergePeaks -d given "
	for path in $outputDir/*_ext.tsv
	do
		command+=" $path"
	done
	echo $command

	$command > ${outputDir}/merged_ext.tsv

	# shrink peak boundaries by overlap distance
	echo "python shrinkPeaks.py $outputDir/merged_ext.tsv $outputDir/merged.tsv $overlapDistance"
	python shrinkPeaks.py $outputDir/merged_ext.tsv $outputDir/merged.tsv $overlapDistance
	rm $outputDir/merged_ext.tsv

	# produce bed file for visualization for merged region
	
	pos2bed.pl $outputDir/merged.tsv > $outputDir/merged.bed

	# find motifs for merged regions
	if $findMotifs
	then	
		findMotifsGenome.pl $outputDir/merged.tsv mm9 $outputDir/mergedMotifs/ -size 200
	fi
	
	# compute overlapping groups
	echo "computing stats for overlapping groups"
	python calcGroupStats.py $outputDir/merged.tsv > $outputDir/group_stats.tsv
	
	if [ -f $outputDir/factorNameMapping ]
	then
		python relabelGroupStats.py $outputDir/group_stats.tsv > $outputDir/group_stats_relabelled.tsv

	fi

	# create human readable file
	command="python makeSummaryFile.py"
	if [ -f $outputDir/factorNameMapping.tsv ]
	then
		command+=" 1"
	else
		command+=" 0"
	fi
	command+=" $outputDir/merged.tsv"
	command+=" $outputDir/group_stats.tsv"
	command+=" $outputDir/motif_stats.tsv"
	for path in $outputDir/*_filteredPeaks.tsv
	do
		[ -f "${path}" ] || continue
		command+=" "$path
	done
	if [ -f $outputDir/factorNameMapping.tsv ]
	then
		command+=" $outputDir/factorNameMapping.tsv" # factorNameMapping file is not created automatically!
	fi
	$command > $outputDir/group_summary.tsv
	echo $command

	# create different peak files for each group
	rm -rf $outputDir/splitPeaks
	mkdir $outputDir/splitPeaks
	echo "python splitMergedPeaks.py $outputDir/merged.tsv $outputDir/group_stats.tsv $outputDir/splitPeaks"
	python splitMergedPeaks.py $outputDir/merged.tsv $outputDir/group_stats.tsv $outputDir/splitPeaks

	echo "creating visualizations" 

	# create a graph visualizing the hierarchy of the groups
	python createHierarchyTree.py $outputDir/group_stats.tsv $outputDir/factorNameMapping.tsv > $outputDir/hierarchy.txt
	dot -Tpng $outputDir/hierarchy.txt > $outputDir/hierarchy.png

	# create a graph visualizing the connectivity of the groups
	python createPeakGraph.py $outputDir/group_stats.tsv > $outputDir/group_connectivity.txt
	circo -Tpng $outputDir/graph_peak.txt > $outputDir/group_connectivity.png

	# create a heat map visualizing the connectivity of the groups
	echo "python makeGroupHeatMap.py $outputDir/group_summary.tsv $outputDir"
	python makeGroupHeatMap.py $outputDir/group_summary.tsv $outputDir
	
	# create a heat map visualizing the peak scores per merged region for all groups
	echo "python makePositionHeatMap.py $outputDir/group_summary.tsv $outputDir/merged.tsv $outputDir/merged"
	python makePositionHeatMap.py $outputDir/group_summary.tsv $outputDir/merged.tsv $outputDir/merged

	# create a heat map visualizing the peak scores per merged region for each individual group
	for path in $outputDir/splitPeaks/groupPeaks*.tsv
	do
		groupNumber=$(basename $path)
		groupNumber=${groupNumber#groupPeaks_}
		groupNumber=${groupNumber%.tsv}
		outPath=${path%%groupPeaks*.tsv}
		outPath+="group_$groupNumber"
		echo "python makePositionHeatMap.py $outputDir/group_summary.tsv $path $outPath"
		python makePositionHeatMap.py $outputDir/group_summary.tsv $path $outPath
	done

	# create a plot summarizing tag densities near merged peaks
	command="annotatePeaks.pl $outputDir/merged.tsv $genome -size 2000 -hist 10 -d"
	for path in $inputPath/*
	do
		[ -d "${path}" ] || continue # if not a directory, skip
		# skip directories that contain input
		if [[ ! $path  =~ .*[iI]{1}nput.* ]]
		then
			if [[ $(basename $path) =~ ^[0-9]-.* ]]
			then
				# append tag directory to command
				command+=" $path"
			fi
		fi
	done

	echo $command
	$($command > $outputDir/mergedPeakDensity.tsv)
	echo "python plotPeakDensity $outputDir/mergedPeakDensity.tsv $outputDir/merged.png $outputDir/factorNameMapping.tsv"
	python plotTagDensity.py $outputDir/mergedTagDensity.tsv $outputDir/merged.png $outputDir/factorNameMapping.tsv

	# plot Tag density for each individual group
	for splitPath in $outputDir/splitPeaks/groupPeaks*.tsv
	do
		command="annotatePeaks.pl $splitPath $genome -size 2000 -hist 10 -d"
		for tagPath in $inputPath/*
		do
			[ -d "${tagPath}" ] || continue # if not a directory, skip
			# skip directories that contain input
			if [[ ! $tagPath  =~ .*[iI]{1}nput.* ]]
			then
				if [[ $(basename $tagPath) =~ ^[0-9]-.* ]]
				then
					# append tag directory to command
					command+=" $tagPath"
				fi
			fi
		done
		echo $command
		groupNumber=$(basename $splitPath)
		groupNumber=${groupNumber#groupPeaks_}
		groupNumber=${groupNumber%.tsv}
		densityOutPath=${splitPath%%groupPeaks*.tsv}
		densityOutPath+="group_$groupNumber"
		densityOutPath+="_TagDensity.tsv"
		echo $densityOutPath
		$($command > $densityOutPath)
		histOutPath=${splitPath%%groupPeaks*.tsv}
		histOutPath+="group_$groupNumber"
		histOutPath+="_TagDensity.png"
		echo "python plotTagDensity $densityOutPath $histOutPath $outputDir/factorNameMapping.tsv"
		python plotTagDensity.py $densityOutPath $histOutPath $outputDir/factorNameMapping.tsv
	done
	
	# test the number of peaks per group
	echo "python assessGroupImportance_peakNumber.py $outputDir/group_stats.tsv $significanceThreshold $outputDir $outputDir/factorNameMapping.tsv"
	python assessGroupImportance_peakNumber.py $outputDir/group_stats.tsv $significanceThreshold $outputDir $outputDir/factorNameMapping.tsv 
	echo "dot -Tpng $outputDir/hierarchy_peakZtest_$significanceThreshold.txt > $outputDir/hierarchy_peakZtest_$significanceThreshold.png"
	dot -Tpng $outputDir/hierarchy_peakZtest_$significanceThreshold.txt > $outputDir/hierarchy_peakZtest_$significanceThreshold.png
fi

### conduct differential motif analysis on overlapping cistromes ###
if $stepThree
then
	echo "conducting motif analysis"
	# finding the motifs can take a while - this should only be done on a computing cluster with qsub installed
	if $cluster
	then
		# try Homer default
		for path in $inputPath/groupPeaks_*.tsv
		do
			command="findMotifsGenome.pl " 
			command+=" "$path 
			outPath=$path 
			outPath=${outPath%.tsv} 
			outPath=${outPath##*/}_default_motifs 
			command+=" $genome ${outputDir}/${outPath}" 
			# create qsub file
			cp qsub_stub.sh $outputDir/qsub_script.sh
			echo $command >> $outputDir/qsub_script.sh
			qsub $outputDir/qsub_script.sh
			rm $outputDir/qsub_script.sh
		done

		# try suggested input
		for path in $outputDir/groupPeaks_*.tsv
		do
			if [ -f $outputDir/filteredInput.tsv ]
			then
				rm $outputDir/filteredInput.tsv
			fi
			groupNumber=$(basename $path)
			groupNumber=${groupNumber##groupPeaks_}
			groupNumber=${groupNumber%%.tsv}
			pythonCommand="python removeOverlapsFromPeakFile.py $outputDir/standardInputPeaks.tsv $path > $outputDir/filteredInput_${groupNumber}.tsv; "
			python removeOverlapsFromPeakFile.py $outputDir/standardInputPeaks.tsv $path > $outputDir/filteredInput_${groupNumber}.tsv
			command="findMotifsGenome.pl " 
			command+=" "$path 
			outPath=$path 
			outPath=${outPath%.tsv} 
			outPath=${outPath##*/}_suggestedInput_motifs
			command+=" mm9 ${outputDir}/${outPath}" 
			command+=" -bg $outputDir/filteredInput_${groupNumber}.tsv -size 200"
			findMotifsGenome.pl $path $genome ${outputDir}/${outPath} -bg $outputDir/filteredInput_${groupNumber}.tsv -size 200
			# create qsub file
			cp qsub_stub.sh $outputDir/qsub_script.sh
			echo $pythonCommand >> $outputDir/qsub_script.sh
			echo $command >> $outputDir/qsub_script.sh
			qsub $outputDir/qsub_script.sh
			rm $outputDir/qsub_script.sh
		done
	fi
	
	# conduct GO analysis on each split peak file
	if $GO
	then
	if [ ! -d $outputDir/GO_analysis ]
	then
		mkdir $outputDir/GO_analysis
	fi
		for path in $outputDir/splitPeaks/groupPeaks*.tsv
		do
			[ -f "${path}" ] || continue
			outpath=$(basename $path)
			outpath=${outpath##groupPeaks}
			outpath=${outpath%%.tsv}
			annotatedPath=$outpath
			annotatedPath="group${annotatedPath}_annotated.tsv"
			outpath="group${outpath}_GO_analysis"
			echo "annotatePeaks.pl $path mm9 -go $outputDir/GO_analysis/$outpath > $outputDir/splitPeaks/$annotatedPath"
			annotatePeaks.pl $path mm9 -go $outputDir/GO_analysis/$outpath > $outputDir/splitPeaks/$annotatedPath
		done
	
		# create bed files for each split group file
		for path in $outputDir/splitPeaks/*_annotated.tsv
		do
			[ -f "${path}" ] || continue
			outpath=$(basename $path)
			outpath=${outpath##groupPeaks}
			outpath=${outpath%%tsv}
			outpath="group${outpath}bed"
			echo "python annotatedPeak2Bed.py $path > $outputDir/splitPeaks/$outpath"
			python annotatedPeak2Bed.py $path > $outputDir/splitPeaks/$outpath
			
		done
		fi


fi


### clean up ###
rm ./*.pos
rm ./*.seq
rm ./*.tmp
