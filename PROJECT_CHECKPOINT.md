# Holstein–Peierls project checkpoint

Updated: 2026-10-07
Branch: `s3-paper1-parameter-campaign`  
Simulation source commit: `34a71f4c57ac8457cc7374d07cbd0bca307a6f57`

## Current state

The S3 midpoint finite-size campaign is complete. The 40x40 campaign completed
28/28 branches; the targeted 20x20 counterpart completed 16/16. All runs had
zero failed branches. Combining the seven new 20x20 coordinates with the three
coordinates already present in the complete 20x20 production map gives **10/10
matched midpoint points** with the same observable topology and classification
at 20x20 and 40x40. Every selected branch converged and every midpoint passed
the linear-Peierls gate at both sizes.

All ten original transition brackets have been narrowed to a half-interval by
their midpoint result. The same sampled transition sequence is present at both
sizes:

| g | U (eV) | transition | refined V1 interval (meV) |
| ---: | ---: | --- | ---: |
| 0.9 | 0.75 | axial → diagonal | 4–8 |
| 0.9 | 0.75 | diagonal → separated | 8–24 |
| 1.0 | 0.525 | onsite → separated | 280–320 |
| 1.0 | 0.75 | axial → diagonal | 10–16 |
| 1.0 | 0.75 | diagonal → separated | 16–28 |
| 1.0 | 1.0 | axial → diagonal | 2–4 |
| 1.0 | 1.0 | diagonal → separated | 10–16 |
| 1.1 | 0.75 | diagonal → separated | 16–28 |
| 1.1 | 1.0 | axial → diagonal | 4–8 |
| 1.1 | 1.0 | diagonal → separated | 12–16 |

These are sampled intervals, not interpolated or exact transition locations.
This remains a targeted competing-branch check, not a global five-seed search.
Positive binding below the frozen 5 meV threshold is marginal and must not be
promoted to robust binding; separated states do not receive a bound-pair label.

## Current milestone: S4 paper data inventory

S3 midpoint refinement is complete. The S4 inventory is recorded in
`docs/s4-paper1-data-inventory-20261007.md` and its machine-readable companion
`docs/s4-paper1-data-inventory-20261007.json`. The audit found that S3 has
reproducible bipolaron results and verified midpoint archives, but this
checkout contains no figure-generation scripts. One-polaron and exciton
inputs, and the S1R raw ensemble, are represented by reports rather than
complete local frozen datasets. Current S3 branch JSON files also do not
contain the spatial fields needed for the planned representative BP lattice
and pair-density maps.

**S4 inventory: complete. Paper-wide data freeze: not ready.** Keep validation
controls explicitly separate from model trends. Next recover and hash the
canonical S3/S1R archives; verify whether the BP spatial fields were archived;
freeze source datasets/manifests for the P and spin-blind X controls; then
create deterministic figure scripts and a single Paper-1 umbrella provenance
manifest linking the distinct sector manifests.

## Canonical artifacts

- 20x20 midpoint manifest: `configs/s3-paper1-bipolaron-boundary-midpoints-20x20-v1.json`
  (SHA-256 `b649d678bac1559709df1477315cfb18dbad2ce5e3917af013311a00de3c0307`)
- 20x20 run: `s3-local-runs/s3-paper1-bipolaron-boundary-midpoints-20x20-v1/20261007T144455Z`
  (16/16 branches)
- 40x40 midpoint manifest: `configs/s3-paper1-bipolaron-boundary-midpoints-40x40-v1.json`
- 40x40 run: `s3-local-runs/s3-paper1-bipolaron-boundary-midpoints-40x40-v1/20260930T102438Z`
  (28/28 branches)
- Reproducible midpoint comparison: `scripts/compare_s3_midpoint_sizes.py`
- Comparison report: `docs/s3-paper1-bipolaron-boundary-midpoints-finite-size-results-20261007.md`
- JSON/CSV comparison products:
  `s3-local-runs/s3-paper1-bipolaron-boundary-midpoints-40x40-v1/20260930T102438Z/comparison/midpoints-20261007/`
- Original coarse-interval reference:
  `docs/s3-paper1-bipolaron-finite-size-comparison-20260930.md`
- Original 20x20 production run:
  `s3-local-runs/s3-paper1-bipolaron-production-20x20-v1/20260928T150000Z`.
- Original targeted 40x40 finite-size run:
  `s3-local-runs/s3-paper1-bipolaron-finite-size-40x40-v1/20260928T183000Z`.
- Original S3 Drive campaign folder:
  `https://drive.google.com/drive/folders/1sLQuIJGFDZoqc9rx9CSTtz6tOEXYwp0y`.
- Original 40x40 manifest / raw archive / report: `1CX2D-wSDc-TDcZW7OD4I9nbCfU8P7l5I` / `1OT04-4gbzPcf0iibnbXKLQvXj8iq3CCf` / `1dvoAJ4QGVOHib6Sk0RJPAzC8hQcMSiQn`.
- Original 20x20-to-40x40 comparison report / reproducibility archive: `1x1_CLThljFLwYvp4aJW7SaTZURD59wYC` / `1qqGo1beNtPzux_FNKdOcynWUpEzT3JAv`.
- Frozen 40x40 midpoint manifest: `1h9z-B69AH9BqINQ0oqQXibpikZ4MSvVp`.
- Campaign Drive folder:
  `https://drive.google.com/drive/folders/1F1HZmCa2-GRGLGIWpGKcIKPKO49liFkI`
- Verified combined raw-data archive: `1Kps1Hdni8LBrMKXjsEDYXCPdbq-FJtNy`
  (`s3-paper1-midpoint-finite-size-20261007.zip`, SHA-256
  `ea0be8f97816642acd02d72420d537369d90386fae558e7b3e808a7893877d1b`).
- Verified results report in Drive: `1Wdk_ee6SIgwF_bEor7hX3P_UlmaWFz8G`.
- Both uploads were verified by listing the campaign folder.

Generated run directories are not committed to Git; the Drive archive contains
the raw branches. The manifests, comparison implementation, results report,
and checkpoint are committed on `s3-paper1-parameter-campaign`; the S3 result
commit is `24c1857`.
