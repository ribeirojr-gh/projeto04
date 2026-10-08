# S3 targeted 20x20 midpoint counterparts (2026-10-07)

## Purpose and scope

The frozen 40x40 midpoint campaign completed ten transition-midpoint
coordinates. Three coordinates were already sampled in the complete 20x20 S3
production map and all three compare as stable at the sampled point. Seven
coordinates were absent from that grid. This campaign supplies same-coordinate
20x20 results for those seven points so the refined brackets can be evaluated
at both sizes.

The seven coordinates and selected seeds exactly mirror the 40x40 midpoint
manifest. This is a targeted cross-size check, not a new global five-seed
search. For each selected minimum, strict convergence and the linear-Peierls
gate remain required. `marginal` binding must not be promoted to robust binding.

| g | U (eV) | V1 (eV) | branches |
| ---: | ---: | ---: | --- |
| 0.9 | 0.75 | 0.024 | diagonal, separated |
| 1.0 | 0.525 | 0.280 | onsite, separated |
| 1.0 | 0.75 | 0.010 | intersite-x, intersite-y, diagonal, separated |
| 1.0 | 0.75 | 0.028 | diagonal, separated |
| 1.0 | 1.0 | 0.010 | diagonal, separated |
| 1.1 | 0.75 | 0.028 | diagonal, separated |
| 1.1 | 1.0 | 0.012 | diagonal, separated |

Total: 7 points and 16 branch relaxations. The frozen manifest is
`configs/s3-paper1-bipolaron-boundary-midpoints-20x20-v1.json`.

## Interpretation limits and next step

Once complete, compare these points with their 40x40 counterparts and report
the sampled topology, branch convergence, binding classification, and
linear-Peierls status at each size. Matching midpoint topology narrows the
sampled transition bracket at both sizes; it does not establish an exact
transition value, a full phase boundary, global root coverage, or robust
binding where the frozen 5 meV threshold is not met. Then update the S3
comparison and checkpoint before the Paper-1 S4 data freeze.
