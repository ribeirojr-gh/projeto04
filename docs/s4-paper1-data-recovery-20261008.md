# S4 — Paper 1 data freeze

Date: 2026-10-08  
Status: **frozen and archived**  
Branch: `s3-paper1-parameter-campaign`

## Archived package

The portable bundle contains the recovered S3/S1R raw results, frozen P/X/BP controls, figure outputs, scripts, configs, and per-file hashes (1,296 files). Unpack it at the repository root to preserve manifest paths.

- [Download the S4 archive](https://drive.google.com/file/d/1kVW5kkL2dzwPa6GFBmfoResfWDiTMcru/view?usp=drivesdk)
- [Drive archive folder](https://drive.google.com/drive/folders/1Aieev8pYinFVUqmvlpgkLbuSPHt8h4f_)
- ZIP size: 5,389,369 bytes
- ZIP SHA-256: `34b52826ee454f43ecb0d1169cd94b4df08cd195f538a434ee7a438ffcc71ea8`
- Per-file bundle manifest: `PAPER1_DATA_BUNDLE_MANIFEST.json` inside the ZIP

## Recovered source data

S3 source archives were verified against their recorded SHA-256 values. The recovered data has 316 converged branch results: 240 production 20×20, 32 targeted 40×40, 16 midpoint 20×20, and 28 midpoint 40×40. The two archive hashes are `27880ac9d7c157be967f7b50e58716bc9385bf946f6f35b22260c496722a7946` (827 ZIP entries) and `ea0be8f97816642acd02d72420d537369d90386fae558e7b3e808a7893877d1b` (151 ZIP entries).

S1R GitHub Actions run [36260401478](https://github.com/ribeirojr-gh/projeto04/actions/runs/36260401478), source commit `6e73becddf3d0c6e85ff97f1db5e4b099ae79ad8`, supplied 104 artifacts. All 104 downloaded archives matched the GitHub API digest. The ensemble contains 102 branch JSON/NPZ pairs (96 singlet roots and 6 triplets), plus aggregate products; spatial arrays were finite.

## Frozen controls and figures

The P/X validation controls have machine-readable NPZ exports and a manifest. BP spatial exports cover onsite, axial, diagonal, and separated 20×20 branches; all four reproduce the source branch energy exactly. The diagonal example remains marginal under the frozen 5 meV binding rule.

Figures 1–6 are provided as PDF, SVG, and PNG in `figures/paper1/`. Their manifest records data/script hashes and interpretation roles. Rendering with Python 3.12.3, Matplotlib 3.11.2, and NumPy 2.5.3 reproduced all 18 output hashes in two consecutive renders. The SVG metadata is deterministic. Figure 7 remains optional and is outside this freeze.

The S3 map is a model trend. P/X and S1R are validation controls, not material predictions. The spin-blind exciton control must not be labelled singlet or triplet.

## Provenance

Machine-readable umbrella provenance: `docs/s4-paper1-data-freeze-manifest-20261008.json`. Figure manifest: `figures/paper1/figure_manifest.json`.
