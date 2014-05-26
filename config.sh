#! /bin/bash

# test variables are here
export testTagDir="/data/mm9/ThioMac/ChIP/NuclearReceptors/NURSA_njs/BMDM.BLRP-PPARg-notx.mm9"
export testDir="/data/mm9/ThioMac/ChIP/NuclearReceptors/NURSA_njs/NR-BLRP-Nathan/BLRP-Nathan-old"
export actualDir="/data/home/nspann/data/mm9/ThioMac/ChIP/NuclearReceptors/NURSA_njs/NR-Jenhan/final_set"
# environment variables are declared here
export home="/data/home/jtao/"

# options for the pipeline
#UCSC visualization (makeUCSCfile, makeBigWig.pl)
export hub="tao"
export genome="mm9"
export generalInput="~/background_test/standardInputPeaks.tsv"
export useControl=true
export updateTags=false
export overlapDistance=200 # bp distance for calculating overlaps
# options for whether or not to run pipeline stages
export makeUCSC=true
export findPeaks=true
export findMotifs=true
export annotatePeaks=true
export quantifyPeaks=true
export cluster=false

# threshold used for filtering peaks
export percentilethreshold="5"
