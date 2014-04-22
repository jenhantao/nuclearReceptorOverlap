#! /bin/bash

# runs the analysis pipeline
source config.sh

# define input variables
inputPath=$1 # path to directory containing all tag directories
stepOne=$2 # run basic analysis for each tag directory
stepTwo=$3 # mege peaks and look for overlapping cistromes
stepThree=$4 # conduct differential motif analysis on overlapping cistromes

if [ ! -d $outputDir ]
then
mkdir $outputDir
fi
unset IFS



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
			command+=" "
			# append tag directory to command
			command+="$path"
		done
		# run commands in the background
		command+=" &"
		echo $command
		$($command)
	fi
	#Peak finding / Transcript detection / Feature identification (findPeaks)
	if $findPeaks 
	then
		echo "finding peaks"
		for path in $inputPath/*
		do
   			[ -d "${path}" ] || continue # if not a directory, skip
			command="findPeaks "
			command+=" "$path
			command+=" -style factor -o $outputDir/$(basename ${path})_peaks.tsv"
			if $useControl
			then
				command+=" -i $control"
			fi
			#command+=" &"
			echo $command
			$($command) > log.txt
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
	command+=" >merged.tsv"
	$command > $outputDir/merged.tsv
	
	# compute overlapping groups
	echo "computing stats for overlapping groups"
	python calcGroupStats.py $outputDir/merged.tsv > $outputDir/group_stats.tsv
fi

### conduct differential motif analysis on overlapping cistromes ###
if $stepThree
then
echo "conducting differential motif analysis"
fi


echo $control
echo "########"
for path in $inputPath/*
do
	[ -f "${path}" ] || continue
	echo ":$path:"
	echo ":$control:"
	if [ $path = $control ]
	then
		echo "CONTRO"
	fi
done
