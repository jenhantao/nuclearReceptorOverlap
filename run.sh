#! /bin/bash

# runs the analysis pipeline
source config.sh

# define input variables
inputPath=$1 # path to directory containing all tag directories
stepOne=$2 # run basic analysis for each tag directory
stepTwo=$3 # mege peaks and look for overlapping cistromes
stepThree=$4 # conduct differential motif analysis on overlapping cistromes

### basic analysis for each the peaks and define cistromes ###
if [ stepOne ]
then
	#UCSC visualization (makeUCSCfile, makeBigWig.pl)
	if [ makeUCSC ] 
	then

	fi
	#Peak finding / Transcript detection / Feature identification (findPeaks)
	if [ makeUCSC ] 
	then

	fi
	#Motif analysis (findMotifsGenome.pl)
	if [ makeUCSC ] 
	then

	fi
	#Annotation of Peaks (annotatePeaks.pl)
	if [ makeUCSC ] 
	then

	fi
	#Quantification of Data at Peaks/Regions in the Genome/Histograms and Heatmaps (annotatePeaks.pl)
	if [ makeUCSC ] 
	then

	fi
	#Quantification of Transcripts and Repeats (analyzeRNA.pl, analyzeRepeats.pl)
	if [ makeUCSC ] 
	then

	fi
fi

### merge the peaks and look for overlapping cistromes ###


### conduct differential motif analysis on overlapping cistromes ###
