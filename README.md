[![DOI](https://img.shields.io/badge/DOI-10.82901%2Fnemar.nm000469-blue)](https://doi.org/10.82901/nemar.nm000469)

# Xie et al. 2026: SEEG of the index PTSD patient before and after right amygdala ablation

Epoched stereo-EEG (157 contacts, 200 Hz, 588 trials, 0.21 h of epochs) from one patient with
post-traumatic stress disorder recorded during a face interpretation-bias task before (`ses-pre`) and after (`ses-post`)
SEEG-guided radiofrequency ablation of the right amygdala. Released by the authors on OSF (https://osf.io/63tym/, CC-BY-NC-4.0)
as `indexPatient.mat` ("de-identified SEEG signals, event markers, and channel information for the index patient") with the
analysis script `analysis_script.m` / `IndexPatient_example_code.m` (in sourcedata).

## Organisation (DatasetType derivative)
- One BrainVision file per session with the released epochs written back-to-back (one `New Segment` marker per trial;
  `events.tsv` gives each trial's position, the authors' trial fields and the trial's index in the released array).
  Epoch window -0.5 to 0.795 s (`eeg.times`), 260 samples at 200 Hz. Signal units are not stated (`units` = n/a; values are the
  released float32 numbers unchanged; the preprocessing is described in the article).
- `electrodes.tsv` (space-Other): coordinates from `chanlocs.tala` (field name suggests Talairach; template not stated in the
  release), with the released per-contact anatomical labels (`annoLab`, e.g. amygdala nuclei) and categories (`annoCat`).
- `participants.tsv`: age and sex are not in the release.

## Privacy
Release described as de-identified; string scan of the MAT file: 1 flagged strings. MAT header export date day set to 01 in sourcedata.
