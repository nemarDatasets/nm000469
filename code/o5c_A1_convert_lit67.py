"""src-literature-67 (OSF 63tym, CC-BY-NC-4.0; Xie et al. 2026 Nat Commun doi:10.1038/s41467-026-74099-5, "Right amygdala ablation
reduces maladaptive negative interpretation bias and symptoms in a patient with PTSD") -> BIDS-iEEG DERIVATIVE (epoched sEEG).
Source: indexPatient.mat: eeg.data (157 ch x 260 samples x 588 trials, float32), eeg.srate 200, eeg.times -500..795 ms,
eeg.chanlocs (labels, electrodeNames, tala xyz, annotation / annoLab / annoCat, eleSel), eeg.event (588: faceName, fear, happy,
em, emRT, validity, cf, cfRT, runNum, session pre/post). Epochs are written back-to-back per session (ses-pre / ses-post).
Usage: python o5c_A1_convert_lit67.py <open500 record dir> <bids root>"""
import json, os, sys
import numpy as np, scipy.io as sio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from o5c_A1_common import write_epochs, events_json, wtsv, wjson, mat_strings, flag_strings, finalize_common, copy_code, copy_sourcedata

REC, OUT = sys.argv[1], sys.argv[2]
P = os.path.join(REC, "files", "indexPatient.mat")
m = sio.loadmat(P, squeeze_me=True, struct_as_record=False)
eeg = m["eeg"]
X = np.asarray(eeg.data)  # (ch, samples, trials)
fs = float(eeg.srate); times = np.asarray(eeg.times, dtype=float).ravel()
nch, nsamp, ntr = X.shape
assert nsamp == times.size
ch = list(np.atleast_1d(eeg.chanlocs)); ev = list(np.atleast_1d(eeg.event))
assert len(ch) == nch and len(ev) == ntr, (len(ch), nch, len(ev), ntr)
def s(v):
    v = np.atleast_1d(v)
    return str(v[0]) if v.size else "n/a"
def num(v):
    v = np.atleast_1d(v).ravel()
    return float(v[0]) if v.size else "n/a"
labels = [s(c.labels) for c in ch]
enames = [s(c.electrodeNames) for c in ch]
tala = [np.asarray(c.tala, dtype=float).ravel() if np.asarray(c.tala).size == 3 else None for c in ch]
anno = [s(c.annoLab) for c in ch]; cat = [s(c.annoCat) for c in ch]; sel = [int(num(c.eleSel)) if num(c.eleSel) != "n/a" else "n/a" for c in ch]
# event fields
cols = ["face_name", "fear_level", "happy_level", "em_key", "em_rt", "validity", "cf_key", "cf_rt", "run", "session"]
rows_all = [[s(e.faceName), num(e.fear), num(e.happy), num(e.em), num(e.emRT), num(e.validity), num(e.cf), num(e.cfRT), int(num(e.runNum)), s(e.session)] for e in ev]
sessions = sorted({r[-1] for r in rows_all}, key=lambda x: {"pre": 0, "post": 1}.get(x, 9))
report = {"recordings": [], "privacy_flags": flag_strings(mat_strings(P)), "sessions": sessions, "n_channels": nch}
scans = {}
for ses in sessions:
    idx = [k for k, r in enumerate(rows_all) if r[-1] == ses]
    trials = [X[:, :, k].T.astype(np.float64) for k in idx]
    sub = "sub-01"; S = f"ses-{ses}"; D = os.path.join(OUT, sub, S, "ieeg")
    stem = f"{sub}_{S}_task-interpretation"
    ev_rows = [rows_all[k][:-1] + [k + 1] for k in idx]
    r = write_epochs(D, stem, trials, fs, labels, ["n/a"] * nch, ["SEEG"] * nch, {
        "TaskName": "interpretation",
        "TaskDescription": "Face-based interpretation-bias task (article): on each trial a face with a mixture of fear and happy expression (fear_level / happy_level, %) was shown and the patient judged the emotion (em key, em_rt) and confidence (cf key, cf_rt). Epochs from -0.5 to 0.795 s around face onset (eeg.times), 200 Hz, from the index patient before (ses-pre) and after (ses-post) SEEG-guided radiofrequency ablation of the right amygdala. Trial details beyond the released event fields are in the article.",
        "Instructions": "n/a (see article)",
        "PowerLineFrequency": 60,
        "SoftwareFilters": {"AuthorsPreprocessing": {"Description": "The release contains preprocessed, epoched signals (float32, 200 Hz); the preprocessing steps are described in the article, not in the release. Values written unchanged."}},
        "HardwareFilters": "n/a",
        "iEEGReference": "n/a (not stated in the release)",
        "iEEGPlacementScheme": "stereo-EEG depth electrodes; per-contact anatomical labels (annoLab / annoCat) and coordinates (tala) are released in eeg.chanlocs",
        "ElectricalStimulation": False, "Manufacturer": "n/a",
    }, ["face_name", "fear_level", "happy_level", "em_key", "em_rt", "validity", "cf_key", "cf_rt", "run", "source_trial_index"], ev_rows,
        ch_extra=[{"description": f"electrode {enames[i]}; {anno[i]} ({cat[i]}); eleSel={sel[i]}", "group": enames[i].rstrip("0123456789")} for i in range(nch)],
        comment=f"o5c_A1_convert_lit67.py: indexPatient.mat eeg.data trials with session={ses}, back-to-back, float32", trial_times=[[times[0] / 1000.0]] * len(idx))
    events_json(os.path.join(D, stem + "_events.json"), {
        "face_name": {"Description": "Stimulus face identifier (event.faceName)"},
        "fear_level": {"Description": "Fear morph level of the face (event.fear)", "Units": "percent"},
        "happy_level": {"Description": "Happy morph level of the face (event.happy)", "Units": "percent"},
        "em_key": {"Description": "Emotion-judgement key code (event.em)"},
        "em_rt": {"Description": "Emotion-judgement reaction time (event.emRT)", "Units": "s"},
        "validity": {"Description": "Trial validity flag (event.validity)"},
        "cf_key": {"Description": "Confidence key code (event.cf)"},
        "cf_rt": {"Description": "Confidence reaction time (event.cfRT)", "Units": "s"},
        "run": {"Description": "Run number (event.runNum)"},
        "source_trial_index": {"Description": "Trial index in the released eeg.data (1-based, both sessions)"}})
    # electrodes
    erows = [[labels[i]] + (["%.4f" % v for v in tala[i]] if tala[i] is not None else ["n/a"] * 3) + ["n/a", enames[i].rstrip("0123456789"), anno[i], cat[i], enames[i]] for i in range(nch)]
    wtsv(os.path.join(D, f"{sub}_{S}_space-Other_electrodes.tsv"), ["name", "x", "y", "z", "size", "group", "anatomical_label", "anatomical_category", "electrode_name"], erows)
    wjson(os.path.join(D, f"{sub}_{S}_space-Other_coordsystem.json"), {
        "iEEGCoordinateSystem": "Other", "iEEGCoordinateUnits": "mm",
        "iEEGCoordinateSystemDescription": "Coordinates copied from eeg.chanlocs.tala of the release (field name suggests Talairach space; the release does not state the template or the localisation method, so the space is recorded as Other). Units assumed mm.",
        "iEEGCoordinateProcessingDescription": "values copied unchanged from chanlocs.tala"})
    r.update(sub=sub, ses=S, stem=stem, n_trials=len(idx))
    report["recordings"].append(r)
    scans.setdefault((sub, S), []).append([f"ieeg/{stem}_ieeg.vhdr", "n/a"])
    print(stem, json.dumps(r), flush=True)
for (sub, S), rows in scans.items():
    wtsv(os.path.join(OUT, sub, S, f"{sub}_{S}_scans.tsv"), ["filename", "acq_time"], sorted(rows))
wjson(os.path.join(OUT, "space-Other_electrodes.json"), {
    "SpatialReference": "n/a (the release gives coordinates in chanlocs.tala without naming the template or reference image)",
    "anatomical_label": {"Description": "Per-contact anatomical annotation from chanlocs.annoLab (e.g. amygdala nucleus), as released"},
    "anatomical_category": {"Description": "Region category from chanlocs.annoCat (e.g. Amy = amygdala), as released"},
    "electrode_name": {"Description": "Original electrode/contact name (chanlocs.electrodeNames)"}})
wtsv(os.path.join(OUT, "participants.tsv"), ["participant_id", "age", "sex", "diagnosis"], [["sub-01", "n/a", "n/a", "post-traumatic stress disorder; drug-resistant epilepsy (index patient of the article)"]])
wjson(os.path.join(OUT, "participants.json"), {"age": {"Description": "not in the release"}, "sex": {"Description": "not in the release"}, "diagnosis": {"Description": "from the article"}})
SD = os.path.join(OUT, "sourcedata", "osf-63tym")
copy_sourcedata([(os.path.join(REC, "files", f), f) for f in sorted(os.listdir(os.path.join(REC, "files"))) if os.path.isfile(os.path.join(REC, "files", f))], SD, scrub=True)
copy_code(OUT, [__file__])
Rr = report["recordings"]; hrs = sum(r["duration_s"] for r in Rr) / 3600
finalize_common(OUT,
    name="Xie2026 amygdala ablation PTSD: epoched stereo-EEG of the index patient before and after right amygdala radiofrequency ablation (interpretation-bias task)",
    dtype="derivative", license_="CC-BY-NC-4.0", authors=["Tao Xie", "Sanne J. H. van Rooij", "Sai Sun", "Noah K. Bryson", "Phillip Demarest", "Haeorum Park", "Luigi Maccotta", "Shuo Wang", "Peter Brunner", "Jon T. Willie"],
    funding=["NIH R01-MH120194", "NIH K01-MH121653", "NIH R01-MH129426", "NIH R01-EB026439, U24-NS109103, U01-NS108916, U01-NS128612, P41-EB018783, R01-EY037195", "American Epilepsy Society Research & Training Fellowship for clinicians", "McDonnell Center for Systems Neuroscience", "Brain & Behavior Research Foundation", "Fondazione Neurone"],
    refs=["https://doi.org/10.1038/s41467-026-74099-5", "https://osf.io/63tym/"],
    howto="Cite Xie T et al. (2026) Right amygdala ablation reduces maladaptive negative interpretation bias and symptoms in a patient with PTSD. Nature Communications, doi:10.1038/s41467-026-74099-5, and the OSF release https://osf.io/63tym/.",
    keywords=["stereo-EEG", "amygdala", "radiofrequency ablation", "PTSD", "interpretation bias", "event-related potentials"],
    source=[{"URL": "https://osf.io/63tym/", "Version": "OSF node 63tym (files as downloaded 2026-10-11; sha256 in sourcedata/osf-63tym/DEIDENTIFICATION_MANIFEST.tsv)"}],
    generated_by=[{"Name": "o5c_A1_convert_lit67.py", "Description": "Repackaging of eeg.data epochs (per session, back-to-back) into BrainVision float32 with the released event fields and chanlocs annotations/coordinates. Code in code/."}],
    ethics=["Collected under the source study's approval (see the article, doi:10.1038/s41467-026-74099-5); the release states the signals are de-identified."],
    readme=f"""# Xie et al. 2026: SEEG of the index PTSD patient before and after right amygdala ablation

Epoched stereo-EEG ({nch} contacts, 200 Hz, {sum(r['n_trials'] for r in Rr)} trials, {hrs:.2f} h of epochs) from one patient with
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
Release described as de-identified; string scan of the MAT file: {len(report['privacy_flags'])} flagged strings. MAT header export date day set to 01 in sourcedata.
""",
    changes_note="BIDS conversion of the OSF 63tym release (Xie et al. 2026) for NEMAR (o5c lane A1).")
json.dump(report, open(os.path.join(OUT, "code", "conversion_report.json"), "w"), indent=1, default=str)
print(json.dumps({"recordings": len(Rr), "hours": hrs, "rt_all": all(r["roundtrip_ok"] for r in Rr), "privacy_flags": report["privacy_flags"][:20], "coords": sum(1 for t in tala if t is not None)}, indent=1))
print("CONVERT_DONE")
