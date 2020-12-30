#!/bin/bash
# Job name:
#SBATCH --job-name=HRL_Geo
#
# Account:
#SBATCH --account=ac_despolab
#
# QoS:
#SBATCH --qos=savio_normal
#
# Partition:
#SBATCH --partition=savio2
#
# Number of tasks:
#SBATCH --ntasks-per-node=1
#
# Processors per task:
#SBATCH --cpus-per-task=20
#
# Nodes
#SBATCH --nodes=1
#
# Memory:
#SBATCH --mem-per-cpu=3200M
#
# Wall clock limit:
#SBATCH --time=4:00:00
#
# Mail type:
#SBATCH --mail-type=all
#
# Mail user:
#SBATCH --mail-user=eichenbaum@berkeley.edu
#
## Command(s) to run (example):
module load gcc openmpi
ht_helper.sh -t /global/scratch/eichenbaum/HRL_Geo/scripts/fmriprep/fmriprep.task -i 006 -L -v
