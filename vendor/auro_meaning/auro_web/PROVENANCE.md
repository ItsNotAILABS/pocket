# auro_web/model.json — provenance (regenerated 2026-10-15)

## What was wrong with the previous file

The previous `model.json` (md5 `581da4ec4eefd61fabf280c05c39122e`, header
`final_loss=1.2026, min_loss=0.5432`) was **mismatched**: its header losses and
its weights came from different training runs. Fresh evaluation of those
weights on their own training corpus gives stream CE **5.7759** (uniform bound
5.5452) — they score ≈4.6 nats worse than their header claims, worse than 100
steps of the shipped trainer, with a per-sentence profile no genuine run of
this code passes through. Full forensic record:
`~/workspace/littlebit-auro/AURO_WEB_V1_FINDINGS.md`.

The original file is preserved beside this one as
**`model.mismatched-orig.json`** (not deleted).

A contributing defect was found and fixed in the trainer at the same time:
`autograd.rms_norm`'s hand-written backward dropped the reduction over the
feature axis in the norm-coupling term (finite-difference max rel err 1.0000).
The corrected backward verifies at max rel err 1.4e-05 against float64 finite
differences. (The fix is byte-identical in every vendored copy of
`autograd.py`: pocket, ResearchersHub, and the legs working copy.)

## What this file is

Regenerated honestly with the **fixed** trainer, forensic control config:

- `AuroTrainer(lr=8e-3, seed=7, hidden_size=128)`, 2000 steps, seq 64,
  ELEMENTS corpus — config identical to the original (vocab 256, hidden 128,
  2 layers, 4 heads, ffn_multiple 4, tied embeddings; 557,696 params).
- Header losses are this run's own prints: **final_loss 1.8018, min_loss
  1.4578** (single-chunk training prints, as `train_text` defines them).
- Pairing verified the forensic way: fresh stream CE of the exported weights
  = **1.9674**, top-1 0.3408 (unpatched-trainer control: stream CE 2.4633;
  the gradient fix accounts for the −0.496-nat improvement).
- Byte-identical copies live in all three locations that carried the old
  file: pocket `vendor/auro_meaning/auro_web/`, ResearchersHub
  `optional/vendor/auro_meaning/auro_web/`, and `~/workspace/legs/auro-web/`.

## HANDOFF

```text
Status: done
Changed: autograd.py (rms_norm backward) in pocket + ResearchersHub + legs;
  auro_web/model.json regenerated in all three; originals preserved as
  model.mismatched-orig.json; this note.
Verified: finite-diff gradient check 1.4e-05; fresh stream CE 1.9674 vs
  header final 1.8018 (honest pairing regime, cf. findings control run).
Blocked by: -
Next agent: compression lane results live in
  ~/workspace/littlebit-auro/RESULTS_AURO_WEB.md.
```
