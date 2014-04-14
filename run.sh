#! /bin/bash

# runs the analysis pipeline
source config.sh

# define input variables
inputPath=$1 # path to directory containing all tag directories
stepOne=$2 # run basic analysis for each tag directory
stepTwo=$3 # mege peaks and look for overlapping cistromes
stepThree=$4 # conduct differential motif analysis on overlapping cistromes

# iterate over each directory and get the 
	for path in $inputPath/*
	do
		[ -e "${path}/tagInfo.txt" ] || continue # if not a directory, skip
		mm9=$(grep $genome $path/tagInfo.txt | wc -l)
		if [ "$mm9" == "0" ]
		then
			echo "WARNING: the following tag directory does not use the genome ${genome}: $path"
		fi
	done


### basic analysis for each the peaks and define cistromes ###
if [ stepOne ]
then
	#UCSC visualization (makeUCSCfile, makeBigWig.pl)
	#if [ makeUCSC ] 
	if [ true ] 
	then
		echo "makeUCSC"
		# iterate over all tag directories and make a hub	
		for path in $inputPath/*
		do
   			[ -d "${path}" ] || continue # if not a directory, skip
    			dirname="$(basename "${path}")"
			echo $dirname
		done
		#makeMultiWigHub.pl $hubName $genome -d $tagDir
	fi
	#Peak finding / Transcript detection / Feature identification (findPeaks)
	if [ findPeaks ] 
	then
		echo "findPeaks"
	fi
	#Motif analysis (findMotifsGenome.pl)
	if [ findMotifs ] 
	then
		echo "findMotifs"
	fi
	#Annotation of Peaks (annotatePeaks.pl)
	if [ annotatePeaks ] 
	then
		echo "annotatePeaks"
	fi
	#Quantification of Data at Peaks/Regions in the Genome/Histograms and Heatmaps (annotatePeaks.pl)
	if [ quantifyPeaks ] 
	then
		echo "quantifyPeaks"
	fi
	#Quantification of Transcripts and Repeats (analyzeRNA.pl, analyzeRepeats.pl)
	if [ quantifyTranscripts ] 
	then
		echo "quantifyTranscripts"
	fi
fi

### merge the peaks and look for overlapping cistromes ###


### conduct differential motif analysis on overlapping cistromes ###
