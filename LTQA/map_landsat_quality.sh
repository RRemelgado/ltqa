#!/bin/bash

# slurm arguments
#SBATCH -J landsat_qa
#SBATCH -t 0-08:00:00
#SBATCH --mem-per-cpu=100G
#SBATCH --array=1982-2022
#SBATCH -o /work/%u/%x-%j-%a_log.txt
#SBATCH -D /work/%u/

# load required modules
module load foss/2018b Python

# execute task
wdir="${SLURM_SUBMIT_DIR}"
metadata=$1
tile_shapefile=$2
land_mask=$3
output_directory=$4
python "$wdir"/map_landsat_quality.py -m "$metadata" -s "$tile_shapefile" -y "$SLURM_ARRAY_TASK_ID" -t day -r "$land_mask" "$output_directory"
