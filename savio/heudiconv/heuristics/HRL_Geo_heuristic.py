import os

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes

def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """
    t1w = create_key('anat/sub-{subject}_T1w')
    task = create_key('func/sub-{subject}_task-Geo_run-{item:03d}_bold')
    fmap = create_key('fmap/sub-{subject}_dir-{item:03d}_epi')

    # t2w = create_key('anat/sub-{subject}_acq-{acq}_T2w')
    # flair = create_key('anat/sub-{subject}_acq-{acq}_FLAIR')
    #rest = create_key('func/sub-{subject}_task-rest_acq-{acq}_run-{item:02d}_bold')

    info = {t1w: [], task: [], fmap: []}

    for idx, seq in enumerate(seqinfo):
        x,y,z,n_vol,protocol,dcm_dir = (seq[6], seq[7], seq[8], seq[9], seq[12], seq[3])

        # t1_mprage --> T1w
        if (z == 176) and (n_vol == 1):
            info[t1w] = [seq[2]]

        # EPI HRL_Geo task --> bold
        if (n_vol == 140):
            info[task].append({'item': seq[2]})

        # Fieldmap --> fmap
        if (n_vol == 2):
            info[fmap].append({'item': seq[2]})

    return info
