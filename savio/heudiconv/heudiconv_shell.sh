for sub in 005 006; do
        heudiconv -d /data/data/dicom/{subject}/*/*.dcm -s ${sub} -f /data/scripts/heudiconv/heuristics/HRL_Geo_heuristic.py -c dcm2niix -o /data/data/bids/${sub} --bids --minmeta
done

END_TIME=$(date);
echo "Heudiconv for subject ${sub} completed at $END_TIME";
