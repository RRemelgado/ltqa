#!/bin/bash

# slurm arguments

#SBATCH -J map_last
#SBATCH -t 0-08:00:00
#SBATCH --mem-per-cpu=30G
#SBATCH --array=1982-2022
#SBATCH -D /work/%u/

# setup job report
#SBATCH -o /work/%u/%x-%j-%a_log.txt

# load required modules
module load foss/2018b Python

# execute task
wdir="${SLURM_SUBMIT_DIR}"
land_mask=$1
data_directory=$2
python "$wdir"/map_last_year.py -y "$SLURM_ARRAY_TASK_ID" -t day -r "$land_mask" "$data_directory"
