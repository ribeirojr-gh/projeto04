# S4 — Paper 1 data inventory and freeze readiness

Date: 2026-10-07  
Branch: `s3-paper1-parameter-campaign`  
Inventory commit before this document: `2886d22`  
Status: **inventory completed; paper-wide data freeze not ready**

## Decision

S3 has a reproducible, finite-size-checked bipolaron result set, but the
current checkout does not yet contain a complete Paper 1 data package or any
figure-generation scripts. Raw S3 run directories are ignored by Git. Some
S3 artifacts are available as Drive archives; the local midpoint comparison
files and their hashes are recorded below. The one-polaron, spin-blind
exciton, and spin-adapted figure inputs are currently represented by
validation documents, not by source data products suitable for figure
reproduction.

Therefore this document is a readiness audit, not a declaration that S4 is
closed. No paper figure should be described as reproducible until its script,
input hashes, source revision, and figure output are frozen together.

## Figure-to-source inventory

| Figure | Intended content | Evidence category | Source/status | Freeze readiness |
| --- | --- | --- | --- | --- |
| 1 | P/BP/direct e-h/spin-adapted model schematic | Model definition / validation context | `docs/research-publication-roadmap-20260923.md`, `docs/paper1-static-readiness-audit-20260926.md`, sector implementations in `src/` | Design can be drafted; no source drawing or generation script |
| 2 | Static one-polaron distortion and localization | Validation control | `docs/t0-polaron-baseline-freeze-20260926.md`; legacy input `examples/static_polaron/parameters1.inc` | No canonical static output, manifest, or figure input found in checkout |
| 3 | Bipolaron U–V topology map | Model trend | S3 frozen configs and results; local midpoint products below; full production archive in Drive (`1qqGo1beNtPzux_FNKdOcynWUpEzT3JAv`) | Strongest candidate, but full production raw data is not in checkout and no plot script exists |
| 4 | Representative BP lattice distortion and pair density | Model trend / examples | S3 branch JSON stores scalar observables (probabilities, separation, energies, gates), not full lattice/pair-density fields | Required fields not found in current branch outputs; requires suitable archived raw fields or a dedicated rerun/export |
| 5 | Spin-blind exciton Frenkel/CT topology and binding | Validation control unless a new production manifest is defined | `docs/static-exciton-validation-results.md`; `experiments/exciton_reference_branch_benchmark.py` | Existing report contains aggregate tables, but no frozen machine-readable source dataset or plot script found |
| 6 | Spin-adapted S/T densities, distortions, and energy relation | Validation control | `docs/s1r-final-github-validation-20260926.md`, `docs/spin-adapted-s0-isotropic-control.md`, S1R implementation and validation records | Raw 102-branch S1R ensemble is not in checkout; report numbers alone are insufficient for maps |
| 7 | Schematic linking direct e-h reference and exchange-resolved sectors | Interpretation / model boundary | `docs/static-exciton-reference-model.md`, `docs/spin-adapted-exciton-observables-design.md` | Optional; no generation script or frozen data source |

Validation controls and physical/model trends must remain separate in captions
and data metadata. In particular, the exciton and 4x4 spin-adapted values
listed above are generic numerical controls, not material predictions. The
spin-blind e-h solver cannot be labelled singlet or triplet. The accepted
spin-adapted S0 benchmark uses harmonic-preconditioned Newton/Armijo; do not
claim that every spin-adapted result used RPROP.

## Local S3 products verified

The two local midpoint runs contain 16/16 (20x20) and 28/28 (40x40) branch
JSON files, plus manifests, provenance, summaries, and CSV/JSON comparison
products. These run directories are ignored by Git. Their simulation
provenance records source commit `34a71f4c57ac8457cc7374d07cbd0bca307a6f57`,
Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1, and single-thread BLAS settings.

Key local artifact SHA-256 values:

| Artifact | SHA-256 |
| --- | --- |
| 20x20 manifest | `b649d678bac1559709df1477315cfb18dbad2ce5e3917af013311a00de3c0307` |
| 20x20 midpoint `points.csv` | `2ded120bed27e204053d6b1600ccf1290089057dfefd6fd90425c038428d7a59` |
| 20x20 summary | `f2e5492bfd8594b3f49504b88cf2ee5d388354af842aa5e0ec5f1d99dedb89ec` |
| 40x40 manifest | `ce6ed237ff0f0658e0e952a7394f47b40271ff675c5fe47fadea58e1609336ba` |
| 40x40 midpoint comparison JSON | `9766ac5a56f881647ac92e8d2c3d34bf08cdf939b6f763cc4bb1e8906049b95e` |
| 40x40 midpoint points CSV | `129fbc99aaa73025108e8caa09a6d62d4c67ea7bbc3bd4ef0a42c8d6f953be78` |
| Refined transition brackets CSV | `0dcbc209019b6521a77286058899fc5a5baa3820b8aea3ddca4051736ed14226` |

The complete combined midpoint raw archive is in Drive as
`1Kps1Hdni8LBrMKXjsEDYXCPdbq-FJtNy` (ZIP SHA-256 recorded in
`PROJECT_CHECKPOINT.md`). The broader 20x20/40x40 comparison archive is
`1qqGo1beNtPzux_FNKdOcynWUpEzT3JAv`. The latter's internal contents have not
yet been unpacked and individually hashed in this audit; it is not treated as
a verified source for Figure 4's spatial fields.

## Next S4 work, in order

1. Recover and unpack canonical raw archives for the complete S3 production
   map and the S1R ensemble; record each file hash and original manifest.
2. Check whether any archived BP branch contains full coordinate and pair
   density arrays. If not, add an immutable production export/rerun for the
   representative configurations selected for Figure 4.
3. Create machine-readable frozen datasets for the polaron and reference
   exciton controls, with explicit `validation_control` labels and manifests.
4. Build the Paper 1 umbrella provenance manifest linking sector manifests,
   source commit(s), solver/optimizer labels, and input hashes. Preserve the
   individual sector manifests because their Hamiltonians differ.
5. Implement deterministic figure scripts that consume only frozen data and
   emit named PDF/SVG/PNG outputs plus a figure provenance record.
6. Re-run each figure from a clean checkout and compare output hashes before
   declaring S4 frozen.
