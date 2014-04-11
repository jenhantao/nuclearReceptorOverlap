#! /bin/bash

# environment variables are declared here
export home="/data/home/jtao/"
export outputDir="${home}/output/"

# options for the pipeline
#UCSC visualization (makeUCSCfile, makeBigWig.pl)
export makeUCSC=true
export findPeaks=true
export findMotifs=true
export annotatePeaks=true
export quantifyPeaks=true
export quantifyTranscripts=true
