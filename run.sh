#! /bin/bash

# runs the analysis pipeline
source config.sh

# define input variables
inputPath=$1 # path to directory containing all tag directories
outputDir=$2 # path to the output directory
stepOne=$3 # run basic analysis for each tag directory
stepTwo=$4 # mege peaks and look for overlapping cistromes
stepThree=$5 # conduct differential motif analysis on overlapping cistromes

if [ ! -d $outputDir ]
then
mkdir $outputDir
fi



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
		done
	fi

	#Motif analysis (findMotifsGenome.pl)
	if $findMotifs
	then
		echo "finding motifs"
		for path in $outputDir/*tsv
		do
   			[ -f "${path}" ] || continue
			command="findMotifsGenome.pl "
			command+=" "$path
			# run commands in the background
			outPath=$path
			outPath=${outPath%_peaks.tsv}
			outPath=${outPath##*/}_motifs
			command+=" $genome ${outputDir}/${outPath}"
			echo $command
			$($command)
		done

	fi
	#Annotation of Peaks (annotatePeaks.pl)
	if $annotatePeaks
	then
		echo "annotating peaks"
		for path in $outputDir/*_peaks.tsv
		do
   			[ -f "${path}" ] || continue
			command="annotatePeaks.pl"
			command+=" "$path
			# run commands in the background
			outPath=$path
			outPath=${outPath%_peaks.tsv}
			outPath=${outPath##*/}_annotatedPeaks.tsv
			#command+=" $genome > ${outputDir}/${outPath}"
			command+=" $genome"
			echo $command
			$($command > ${outputDir}/${outPath})
		done

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
	for path in $outputDir/*_annotatedPeaks.tsv
	do
		[ -f "${path}" ] || continue
		outPath=$path
		outPath=${outPath%_annotatedPeaks.tsv}
		outPath=${outPath##*/}_ext.tsv
		python extendPeaks.py $path ${outputDir}/${outPath} $overlapDistance
			
	done
	# call merge peaks
	command="mergePeaks -d given "
	for path in $outputDir/*_ext.tsv
	do
		command+=" $path"
	done
	echo $command
	$command > ${outputDir}/merged.tsv

	# produce bed file for visualization for merged region
	pos2bed.pl $outputDir/merged.tsv > $outputDir/peakfile.bed

	# find motifs for merged regions
	if $findMotifs
	then	
		findMotifsGenome.pl $outputDir/merged.tsv mm9 $outputDir/mergedMotifs/ -size 200
	fi
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
	command+=" -m $outputDir/mergedMotifs/homerMotifs.all.motifs"
	echo $command
	$command > $outputDir/merged_annotated.tsv
	
	# compute overlapping groups
	echo "computing stats for overlapping groups"
	python calcGroupStats.py $outputDir/merged.tsv > $outputDir/group_stats.tsv

	# create different peak files for each group
	python splitMergedPeaks.py $outputDir/merged_annotated.tsv $outputDir/group_stats.tsv $outputDir

	# create a graph visualizing the hierarchy of the groups
	python createHierarchyTree.py $outputDir/group_stats.tsv >$outputDir/hierarchy.txt
	neato -Tpng $outputDir/hierarchy.txt > $outputDir/hierarchy.png

	# create a graph visualizing the connectivity of the groups
	python createPeakGraph.py $outputDir/group_stats.tsv > $outputDir/graph_peak.txt
	circo -Tpng $outputDir/graph_peak.txt > $outputDir/graph_peak.png

fi

### conduct differential motif analysis on overlapping cistromes ###
if $stepThree
then
echo "conducting motif analysis"
# this step would be quite slow
# conduct motif analysis for each group
#for path in $outputDir/groupPeaks_*.tsv
#do
#	[ -f "${path}" ] || continue
#	command="findMotifsGenome.pl "
#	command+=" "$path
#	# run commands in the background
#	outPath=$path
#	outPath=${outPath%.tsv}
#	outPath=${outPath##*/}_motifs
#	command+=" $genome ${outputDir}/${outPath}"
#	echo $command
#	$($command)
#done

fi


