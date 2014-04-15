#! /bin/bash

# runs the analysis pipeline
source config.sh

# define input variables
inputPath=$1 # path to directory containing all tag directories
stepOne=$2 # run basic analysis for each tag directory
stepTwo=$3 # mege peaks and look for overlapping cistromes
stepThree=$4 # conduct differential motif analysis on overlapping cistromes
echo $outputDir
if [ ! -d $outputDir ]
then
mkdir $outputDir
fi

for path in $inputPath/*
do
	[ -e "${path}/tagInfo.txt" ] || continue # if not a directory, skip
	# if mm9 is specified, it should appear in tagInfo.txt at least once
	mm9=$(grep $genome $path/tagInfo.txt | wc -l)
	if [ "$mm9" == "0" ]
	then
		echo "WARNING: the following tag directory does not use the genome ${genome}: $path"
	fi
done


### basic analysis for each the peaks and define cistromes ###
if $stepOne
then
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
			command+=" $genome $outPath"
			echo $command
			$($command)
		done

	fi
	#Annotation of Peaks (annotatePeaks.pl)
	if $annotatePeaks
	then
		echo "annotatePeaks"
	fi
	#Quantification of Data at Peaks/Regions in the Genome/Histograms and Heatmaps (annotatePeaks.pl)
	if $quantifyPeaks 
	then
		echo "quantifyPeaks"
	fi
	#Quantification of Transcripts and Repeats (analyzeRNA.pl, analyzeRepeats.pl)
	if $quantifyTranscripts
	then
		echo "quantifyTranscripts"
	fi
fi

### merge the peaks and look for overlapping cistromes ###


### conduct differential motif analysis on overlapping cistromes ###