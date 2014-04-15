#! /bin/bash

# test variables are here
export testTagDir="/data/mm9/ThioMac/ChIP/NuclearReceptors/NURSA_njs/BMDM.BLRP-PPARg-notx.mm9"
export testDir="/data/mm9/ThioMac/ChIP/NuclearReceptors/NURSA_njs/NR-BLRP-Nathan/BLRP-Nathan-old"
# environment variables are declared here
export home="/data/home/jtao/"
export outputDir="${home}/output/"

# options for the pipeline
#UCSC visualization (makeUCSCfile, makeBigWig.pl)
export hub="tao"
export genome="mm9"
export control="/data/mm9/ThioMac/ChIP/NuclearReceptors/NURSA_njs/NR-BLRP-Nathan/BLRP-Nathan-old/BirA-input-Nathan/"
export useControl=true
export updateTags=true
# options for whether or not to run pipeline stages
export makeUCSC=false
export findPeaks=false
export findMotifs=false
export annotatePeaks=true
export quantifyPeaks=true
export quantifyTranscripts=true
