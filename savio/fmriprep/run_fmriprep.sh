export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK;

singularity run -B /global/scratch/eichenbaum/HRL_Geo/data/:/home/fmriprep /global/scratch/eichenbaum/singularityIMG/fmriprep/kasbohm-singularity_fmriprep-master-1.5.0.simg \
       /home/fmriprep/bids \
       /home/fmriprep \
       participant \
       --participant-label $HT_TASK_ID \
        --nthreads 20 \
       --omp-nthreads 10 \
       --mem_mb 64000 \
       --ignore fieldmaps sbref \
       --bold2t1w-dof 9 \
       --output-spaces T1w MNI152NLin2009cAsym \
       --fs-license-file /home/fmriprep/fs_license.txt \
       -w /home/fmriprep/work \
       --write-graph \
       --skip_bids_validation \
       --fs-no-reconall

echo "Finished FMRIPREP run attempt for subject $SUB_ID."

