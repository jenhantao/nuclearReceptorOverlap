#!/bin/bash
#PBS -q hotel
#PBS -N group_motifs
#PBS -l nodes=1:ppn=8
#PBS -l walltime=6:00:00
#PBS -o /oasis/tscc/scratch/vlink/cluster/output.txt
#PBS -e /oasis/tscc/scratch/vlink/cluster/error.txtg
#PBS -V
#PBS -M jtao@ucsd.edu
#PBS -m n
#PBS -A glass-group

cd /oasis/tscc/scratch/vlink/cluster/
