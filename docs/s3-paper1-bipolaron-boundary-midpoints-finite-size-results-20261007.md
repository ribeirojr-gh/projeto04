# S3 matched 20x20/40x40 midpoint results (2026-10-07)

## Outcome

All **10 of 10 midpoint points** have matching observable topology and classification at 20x20 and 40x40. Both sizes converge all selected branches and pass the linear-Peierls gate at every midpoint. No branch failures occurred in either campaign.

This is a targeted competing-branch comparison, not a global five-seed search. Topology agreement at the midpoint narrows the sampled interval; it does not locate an exact transition or establish global phase-boundary convergence. Bound midpoint states with positive binding below the frozen 5 meV threshold remain marginal; separated states are not assigned a bound-pair classification.

## Matched midpoint points

| g | U (eV) | V1 (meV) | topology at both sizes | binding 20x20 (meV) | binding 40x40 (meV) | status |
| ---: | ---: | ---: | --- | ---: | ---: | --- |
| 0.9 | 0.750 | 4.0 | axial | 4.323 | 4.617 | stable_at_sampled_point |
| 0.9 | 0.750 | 24.0 | separated | 0.000 | 0.000 | stable_at_sampled_point |
| 1.0 | 0.525 | 280.0 | onsite | 1.330 | 1.302 | stable_at_sampled_point |
| 1.0 | 0.750 | 10.0 | axial | 1.011 | 1.309 | stable_at_sampled_point |
| 1.0 | 0.750 | 28.0 | separated | 0.000 | 0.000 | stable_at_sampled_point |
| 1.0 | 1.000 | 2.0 | axial | 1.986 | 2.168 | stable_at_sampled_point |
| 1.0 | 1.000 | 10.0 | diagonal | 0.309 | 0.332 | stable_at_sampled_point |
| 1.1 | 0.750 | 28.0 | separated | 0.000 | 0.000 | stable_at_sampled_point |
| 1.1 | 1.000 | 4.0 | axial | 2.173 | 2.368 | stable_at_sampled_point |
| 1.1 | 1.000 | 12.0 | diagonal | 0.128 | 0.140 | stable_at_sampled_point |

## Refined sampled transition intervals

| g | U (eV) | transition | original interval (meV) | refined interval (meV) |
| ---: | ---: | --- | ---: | ---: |
| 0.9 | 0.750 | axial -> diagonal | 0.0–8.0 | 4.0–8.0 |
| 0.9 | 0.750 | diagonal -> separated | 8.0–40.0 | 8.0–24.0 |
| 1.0 | 0.525 | onsite -> separated | 240.0–320.0 | 280.0–320.0 |
| 1.0 | 0.750 | axial -> diagonal | 4.0–16.0 | 10.0–16.0 |
| 1.0 | 0.750 | diagonal -> separated | 16.0–40.0 | 16.0–28.0 |
| 1.0 | 1.000 | axial -> diagonal | 0.0–4.0 | 2.0–4.0 |
| 1.0 | 1.000 | diagonal -> separated | 4.0–16.0 | 10.0–16.0 |
| 1.1 | 0.750 | diagonal -> separated | 16.0–40.0 | 16.0–28.0 |
| 1.1 | 1.000 | axial -> diagonal | 0.0–8.0 | 4.0–8.0 |
| 1.1 | 1.000 | diagonal -> separated | 8.0–16.0 | 12.0–16.0 |

These ten refined intervals retain the same sampled topology sequence at both sizes. They are not interpolated transition energies.

## Provenance

- Simulation source commit: `34a71f4c57ac8457cc7374d07cbd0bca307a6f57`
- 20x20 manifest: `configs/s3-paper1-bipolaron-boundary-midpoints-20x20-v1.json` (SHA-256 `b649d678bac1559709df1477315cfb18dbad2ce5e3917af013311a00de3c0307`)
- 40x40 manifest: `configs/s3-paper1-bipolaron-boundary-midpoints-40x40-v1.json` (SHA-256 `a23ec12f0583fe0ff2694708bcf54173bd8ddd5c77788c40cf8c1272f54212a5`)
- 20x20 summary SHA-256: `f2e5492bfd8594b3f49504b88cf2ee5d388354af842aa5e0ec5f1d99dedb89ec`
- 40x40 summary SHA-256: `0131e35e53f2d6ff952b1f7e0d6c671da8b148946b4638f9725d1f1469d4d1af`
- Prior three-point comparison: `s3-local-runs/s3-paper1-bipolaron-boundary-midpoints-40x40-v1/20260930T102438Z/comparison/finite_size_comparison.json` (SHA-256 `7780bb391d5b23d4df0f11b1c8eea9df33201c84642866fd1c75c2012f5b2153`)
- Comparison script SHA-256: `6e41eb3efad1246f8c5458d403c8d47594370eb0f1edd389e181ec9c3eeb6ea9`
- Original coarse brackets: `docs/s3-paper1-bipolaron-finite-size-comparison-20260930.md`.
