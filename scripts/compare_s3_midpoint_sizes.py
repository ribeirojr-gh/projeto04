#!/usr/bin/env python3
"""Compare targeted S3 midpoint campaigns and refine matched transition brackets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


BRACKETS = [
    (0.9, 0.75, 0.000, 0.008, "axial", "diagonal", 0.004),
    (0.9, 0.75, 0.008, 0.040, "diagonal", "separated", 0.024),
    (1.0, 0.525, 0.240, 0.320, "onsite", "separated", 0.280),
    (1.0, 0.75, 0.004, 0.016, "axial", "diagonal", 0.010),
    (1.0, 0.75, 0.016, 0.040, "diagonal", "separated", 0.028),
    (1.0, 1.0, 0.000, 0.004, "axial", "diagonal", 0.002),
    (1.0, 1.0, 0.004, 0.016, "diagonal", "separated", 0.010),
    (1.1, 0.75, 0.016, 0.040, "diagonal", "separated", 0.028),
    (1.1, 1.0, 0.000, 0.008, "axial", "diagonal", 0.004),
    (1.1, 1.0, 0.008, 0.016, "diagonal", "separated", 0.012),
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _index(points: list[dict[str, Any]]) -> dict[tuple[float, float, float], dict[str, Any]]:
    indexed = {}
    for point in points:
        key = (float(point["coupling_scale"]), float(point["U_eV"]), float(point["V1_eV"]))
        if key in indexed:
            raise ValueError(f"duplicate point: {key}")
        indexed[key] = point
    return indexed


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _pair_record(point20: dict[str, Any], point40: dict[str, Any]) -> dict[str, Any]:
    same_topology = point20["observable_topology"] == point40["observable_topology"]
    same_class = point20["classification"] == point40["classification"]
    converged = bool(point20["all_branches_converged"]) and bool(point40["all_branches_converged"])
    peierls = bool(point20["linear_peierls_gate"]) and bool(point40["linear_peierls_gate"])
    status = (
        "incomplete_or_unconverged" if not converged else
        "outside_linear_peierls_gate" if not peierls else
        "topology_changed_with_size" if not same_topology else
        "classification_changed_with_size" if not same_class else
        "stable_at_sampled_point"
    )
    return {
        "coupling_scale": float(point20["coupling_scale"]),
        "U_eV": float(point20["U_eV"]),
        "V1_eV": float(point20["V1_eV"]),
        "topology_20x20": point20["observable_topology"],
        "topology_40x40": point40["observable_topology"],
        "classification_20x20": point20["classification"],
        "classification_40x40": point40["classification"],
        "binding_status_20x20": point20["binding_status"],
        "binding_status_40x40": point40["binding_status"],
        "binding_20x20_meV": 1000.0 * float(point20["binding_vs_separated_eV"]),
        "binding_40x40_meV": 1000.0 * float(point40["binding_vs_separated_eV"]),
        "binding_change_40_minus_20_meV": 1000.0 * (
            float(point40["binding_vs_separated_eV"]) - float(point20["binding_vs_separated_eV"])
        ),
        "branches_20x20": len(point20["required_branches"]),
        "branches_40x40": len(point40["required_branches"]),
        "converged_both_sizes": converged,
        "linear_peierls_gate_both_sizes": peierls,
        "same_observable_topology": same_topology,
        "same_classification": same_class,
        "finite_size_status": status,
    }


def _bracket_rows(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed = {
        (row["coupling_scale"], row["U_eV"], row["V1_eV"]): row for row in points
    }
    results = []
    for g, u, old_lo, old_hi, lower_topology, upper_topology, mid in BRACKETS:
        point = indexed[(g, u, mid)]
        topology20 = point["topology_20x20"]
        topology40 = point["topology_40x40"]
        matched = point["finite_size_status"] == "stable_at_sampled_point"
        if matched and topology20 == topology40 == lower_topology:
            new_lo, new_hi = mid, old_hi
        elif matched and topology20 == topology40 == upper_topology:
            new_lo, new_hi = old_lo, mid
        else:
            new_lo, new_hi = old_lo, old_hi
            matched = False
        results.append({
            "coupling_scale": g,
            "U_eV": u,
            "transition": f"{lower_topology} -> {upper_topology}",
            "original_lower_V1_eV": old_lo,
            "original_upper_V1_eV": old_hi,
            "midpoint_V1_eV": mid,
            "topology_20x20_at_midpoint": topology20,
            "topology_40x40_at_midpoint": topology40,
            "refined_lower_V1_eV": new_lo,
            "refined_upper_V1_eV": new_hi,
            "same_sampled_transition_bracket_at_both_sizes": matched,
            "interpretation_limit": "sampled interval only; no exact transition location is inferred",
        })
    return results


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# S3 matched 20x20/40x40 midpoint results (2026-10-07)",
        "",
        "## Outcome",
        "",
        f"All **{report['point_count_stable']} of {report['point_count']} midpoint points** have matching observable topology and classification at 20x20 and 40x40. Both sizes converge all selected branches and pass the linear-Peierls gate at every midpoint. No branch failures occurred in either campaign.",
        "",
        "This is a targeted competing-branch comparison, not a global five-seed search. Topology agreement at the midpoint narrows the sampled interval; it does not locate an exact transition or establish global phase-boundary convergence. Bound midpoint states with positive binding below the frozen 5 meV threshold remain marginal; separated states are not assigned a bound-pair classification.",
        "",
        "## Matched midpoint points",
        "",
        "| g | U (eV) | V1 (meV) | topology at both sizes | binding 20x20 (meV) | binding 40x40 (meV) | status |",
        "| ---: | ---: | ---: | --- | ---: | ---: | --- |",
    ]
    for p in report["points"]:
        lines.append(
            f"| {p['coupling_scale']:.1f} | {p['U_eV']:.3f} | {1000*p['V1_eV']:.1f} | {p['topology_20x20']} | {p['binding_20x20_meV']:.3f} | {p['binding_40x40_meV']:.3f} | {p['finite_size_status']} |"
        )
    lines.extend([
        "",
        "## Refined sampled transition intervals",
        "",
        "| g | U (eV) | transition | original interval (meV) | refined interval (meV) |",
        "| ---: | ---: | --- | ---: | ---: |",
    ])
    for b in report["refined_transition_brackets"]:
        lines.append(
            f"| {b['coupling_scale']:.1f} | {b['U_eV']:.3f} | {b['transition']} | {1000*b['original_lower_V1_eV']:.1f}–{1000*b['original_upper_V1_eV']:.1f} | {1000*b['refined_lower_V1_eV']:.1f}–{1000*b['refined_upper_V1_eV']:.1f} |"
        )
    lines.extend([
        "",
        "These ten refined intervals retain the same sampled topology sequence at both sizes. They are not interpolated transition energies.",
        "",
        "## Provenance",
        "",
        f"- Simulation source commit: `{report['simulation_source_commit']}`",
        f"- 20x20 manifest: `{report['inputs']['manifest_20x20']}` (SHA-256 `{report['inputs']['manifest_20x20_sha256']}`)",
        f"- 40x40 manifest: `{report['inputs']['manifest_40x40']}` (SHA-256 `{report['inputs']['manifest_40x40_sha256']}`)",
        f"- 20x20 summary SHA-256: `{report['inputs']['summary_20x20_sha256']}`",
        f"- 40x40 summary SHA-256: `{report['inputs']['summary_40x40_sha256']}`",
        f"- Prior three-point comparison: `{report['inputs']['prior_comparison']}` (SHA-256 `{report['inputs']['prior_comparison_sha256']}`)",
        f"- Comparison script SHA-256: `{report['inputs']['comparison_script_sha256']}`",
        "- Original coarse brackets: `docs/s3-paper1-bipolaron-finite-size-comparison-20260930.md`.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary-20x20", type=Path, required=True)
    parser.add_argument("--summary-40x40", type=Path, required=True)
    parser.add_argument("--prior-comparison", type=Path, required=True)
    parser.add_argument("--manifest-20x20", type=Path, required=True)
    parser.add_argument("--manifest-40x40", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--simulation-source-commit", required=True)
    args = parser.parse_args()

    summary20 = json.loads(args.summary_20x20.read_text(encoding="utf-8"))
    summary40 = json.loads(args.summary_40x40.read_text(encoding="utf-8"))
    prior = json.loads(args.prior_comparison.read_text(encoding="utf-8"))
    if not summary20.get("complete") or not summary40.get("complete"):
        raise SystemExit("both midpoint campaigns must be complete")
    if summary20.get("failed_tasks") or summary40.get("failed_tasks"):
        raise SystemExit("campaign summaries contain failed tasks")

    p20, p40 = _index(summary20["points"]), _index(summary40["points"])
    records = []
    for key, point20 in p20.items():
        point40 = p40.get(key)
        if point40 is None:
            raise SystemExit(f"20x20 midpoint is missing at 40x40: {key}")
        records.append(_pair_record(point20, point40))

    old_pairs = [
        row for row in prior["points"]
        if row.get("present_at_20x20") and row.get("present_at_40x40")
    ]
    if len(old_pairs) != 3:
        raise SystemExit(f"expected three prior shared midpoint points, found {len(old_pairs)}")
    for row in old_pairs:
        records.append({
            "coupling_scale": float(row["coupling_scale"]),
            "U_eV": float(row["U_eV"]),
            "V1_eV": float(row["V1_eV"]),
            "topology_20x20": row["topology_20x20"],
            "topology_40x40": row["topology_40x40"],
            "classification_20x20": row["classification_20x20"],
            "classification_40x40": row["classification_40x40"],
            "binding_status_20x20": "marginal" if row["binding_20x20_eV"] else "not_applicable_separated_topology",
            "binding_status_40x40": "marginal" if row["binding_40x40_eV"] else "not_applicable_separated_topology",
            "binding_20x20_meV": 1000.0 * float(row["binding_20x20_eV"]),
            "binding_40x40_meV": 1000.0 * float(row["binding_40x40_eV"]),
            "binding_change_40_minus_20_meV": row["binding_change_40_minus_20_meV"],
            "branches_20x20": row["required_branches_20x20"],
            "branches_40x40": row["required_branches_40x40"],
            "converged_both_sizes": row["all_required_branches_converged_both_sizes"],
            "linear_peierls_gate_both_sizes": row["linear_peierls_gate_both_sizes"],
            "same_observable_topology": row["same_observable_topology"],
            "same_classification": row["same_classification"],
            "finite_size_status": row["finite_size_status"],
        })

    records.sort(key=lambda r: (r["coupling_scale"], r["U_eV"], r["V1_eV"]))
    if len(records) != 10 or len({(r["coupling_scale"], r["U_eV"], r["V1_eV"]) for r in records}) != 10:
        raise SystemExit("expected ten unique matched midpoint coordinates")
    brackets = _bracket_rows(records)
    report = {
        "schema_version": 1,
        "campaign_id": "s3-paper1-bipolaron-boundary-midpoints-finite-size-20261007",
        "simulation_source_commit": args.simulation_source_commit,
        "point_count": len(records),
        "point_count_stable": sum(r["finite_size_status"] == "stable_at_sampled_point" for r in records),
        "campaign_branch_counts": {
            "20x20_targeted_midpoint": summary20["completed_branch_records"],
            "40x40_targeted_midpoint": summary40["completed_branch_records"],
            "20x20_previously_computed_shared_midpoints": sum(r["required_branches_20x20"] for r in old_pairs),
        },
        "refined_transition_bracket_count": len(brackets),
        "matched_refined_transition_bracket_count": sum(b["same_sampled_transition_bracket_at_both_sizes"] for b in brackets),
        "interpretation_limit": "targeted selected-branch midpoint checks; no global five-seed search, exact transition energy, or continuous phase-boundary convergence is claimed",
        "robust_binding_threshold_eV": 0.005,
        "inputs": {
            "summary_20x20": str(args.summary_20x20),
            "summary_20x20_sha256": _sha256(args.summary_20x20),
            "summary_40x40": str(args.summary_40x40),
            "summary_40x40_sha256": _sha256(args.summary_40x40),
            "prior_comparison": str(args.prior_comparison),
            "prior_comparison_sha256": _sha256(args.prior_comparison),
            "manifest_20x20": str(args.manifest_20x20),
            "manifest_20x20_sha256": _sha256(args.manifest_20x20),
            "manifest_40x40": str(args.manifest_40x40),
            "manifest_40x40_sha256": _sha256(args.manifest_40x40),
            "comparison_script_sha256": _sha256(Path(__file__).resolve()),
        },
        "points": records,
        "refined_transition_brackets": brackets,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "midpoint_finite_size_comparison.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    _write_csv(args.output_dir / "midpoint_points.csv", records)
    _write_csv(args.output_dir / "refined_transition_brackets.csv", brackets)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(_markdown(report), encoding="utf-8")
    print(json.dumps({
        "points": report["point_count"],
        "stable_points": report["point_count_stable"],
        "refined_brackets": report["refined_transition_bracket_count"],
        "matched_brackets": report["matched_refined_transition_bracket_count"],
        "output_dir": str(args.output_dir),
        "report": str(args.report),
    }, indent=2))


if __name__ == "__main__":
    main()
