#!/bin/bash

#SBATCH -D /work/remelgad/
#SBATCH -J LTQA
#SBATCH -t 0-24:00:00
#SBATCH --mem-per-cpu=100G
#SBATCH -o /work/remelgad/%x-%j-%a_log.txt

# load required modules
module load foss/2018b R/3.6.0

# execute task
Rscript --vanilla "${SLURM_SUBMIT_DIR}"/main.R
