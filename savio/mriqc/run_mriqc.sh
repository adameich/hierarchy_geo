export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK;

singularity run -B /global/scratch/eichenbaum/HRL_Geo/data/:/data /global/scratch/eichenbaum/singularityIMG/mriqc/poldracklab_mriqc_latest-2018-08-16-d603c9d96dbe.img \
       /data/bids \
       /data/mriqc \
       participant \
       --participant-label $HT_TASK_ID \
       --modalities T1w bold \
       --verbose-reports \
       --n_procs 20 \
       --mem_gb 64 \
       --hmc-afni \
       --ants-nthreads 10 \
       --float32 \
       -w /data/work

echo "Finished MRIQC run attempt for subject $SUB_ID."

