#!/usr/bin/env python3
"""Render the frozen Paper 1 static figures and record input/output hashes."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


COLORS = {
    "onsite": "#5b8e7d",
    "axial": "#3f78a8",
    "diagonal": "#db9c32",
    "separated": "#8d6cab",
    "mixed": "#777777",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def save_figure(fig: plt.Figure, path: Path, title: str) -> list[dict[str, object]]:
    outputs = []
    metadata = {"Creator": "Holstein-Peierls Paper 1 reproducible figure script", "Title": title}
    for suffix in ("pdf", "svg", "png"):
        output = path.with_suffix(f".{suffix}")
        format_metadata = dict(metadata)
        if suffix == "pdf":
            format_metadata.update({"CreationDate": None, "ModDate": None})
        elif suffix == "svg":
            format_metadata["Date"] = None
        elif suffix == "png":
            format_metadata = {"Software": metadata["Creator"], "Title": title}
        fig.savefig(output, format=suffix, dpi=300, metadata=format_metadata)
        outputs.append({"path": output.name, "sha256": sha256(output), "size_bytes": output.stat().st_size})
    plt.close(fig)
    return outputs


def image_panel(ax, array, title, cmap="viridis", *, center_zero=False, cbar_label=None):
    values = np.asarray(array)
    limits = {}
    if center_zero:
        scale = max(float(np.max(np.abs(values))), 1e-12)
        limits = {"vmin": -scale, "vmax": scale}
    artist = ax.imshow(values, origin="lower", cmap=cmap, interpolation="nearest", **limits)
    ax.set_title(title)
    ax.set_xlabel("x (lattice sites)")
    ax.set_ylabel("y (lattice sites)")
    ax.set_aspect("equal")
    colorbar = ax.figure.colorbar(artist, ax=ax, fraction=0.046, pad=0.04)
    if cbar_label:
        colorbar.set_label(cbar_label)
    return artist


def relative_exciton_density(pair_probability: np.ndarray) -> np.ndarray:
    ny, nx, _, _ = pair_probability.shape
    relative = np.zeros((ny, nx), dtype=np.float64)
    for dy in range(ny):
        for dx in range(nx):
            relative[dy, dx] = sum(
                pair_probability[ey, ex, (ey + dy) % ny, (ex + dx) % nx]
                for ey in range(ny)
                for ex in range(nx)
            )
    return relative


def figure_1(output: Path):
    fig, ax = plt.subplots(figsize=(12, 5.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")
    boxes = [
        (0.35, "P", "One charge", "Holstein + Peierls\nstatic lattice relaxation", "#e4f1ed"),
        (3.25, "BP", "Two equal charges", "Onsite U + offsite V\ncorrelated singlet pair", "#e7eef8"),
        (6.15, "X reference", "Distinguishable e–h", "Direct attraction\nspin blind", "#fff0d9"),
        (9.05, "SA", "Neutral reference", "Exchange resolved\nopen shell S / T", "#eee7f5"),
    ]
    for x, acronym, heading, detail, fill in boxes:
        rect = plt.Rectangle((x, 2.15), 2.55, 2.7, facecolor=fill, edgecolor="#32414a", linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + 1.275, 4.35, acronym, ha="center", va="center", fontsize=17, weight="bold")
        ax.text(x + 1.275, 3.7, heading, ha="center", va="center", fontsize=11, weight="bold")
        ax.text(x + 1.275, 2.85, detail, ha="center", va="center", fontsize=10, linespacing=1.4)
    ax.text(6, 5.55, "Static extended Holstein–Peierls sectors", ha="center", fontsize=18, weight="bold")
    ax.text(6, 1.35, "Shared lattice model; distinct particle spaces and interaction conventions", ha="center", fontsize=12)
    ax.text(7.425, 0.62, "The spin-blind e–h reference is not a singlet/triplet calculation.", ha="center", fontsize=10, color="#6b2f2f")
    return save_figure(fig, output / "figure-1-model-sectors", "Paper 1 model sectors")


def figure_2(root: Path, output: Path, inputs: list[Path]):
    inputs.extend((
        root / "configs/s4-paper1-reference-controls-v1.json",
        root / "paper1-local-data/validation-controls/generic-exciton-10x10-20261008-7ce26e7/manifest.json",
    ))
    data = root / "paper1-local-data/validation-controls/generic-exciton-10x10-20261008-7ce26e7/polaron-20x20.npz"
    inputs.append(data)
    with np.load(data, allow_pickle=False) as arrays:
        fig, axes = plt.subplots(1, 2, figsize=(9, 4.2), constrained_layout=True)
        image_panel(axes[0], arrays["charge_density"], "One-polaron charge density", "viridis", cbar_label="site probability")
        image_panel(axes[1], arrays["lattice_u_A"], "Holstein distortion u", "coolwarm", center_zero=True, cbar_label="Å")
    return save_figure(fig, output / "figure-2-polaron-reference", "Static one-polaron validation control")


def figure_3(root: Path, output: Path, inputs: list[Path]):
    source = root / "s3-local-runs/s3-paper1-bipolaron-production-20x20-v1/20260928T150000Z/points.csv"
    inputs.extend((
        source,
        root / "configs/s3-paper1-bipolaron-production-20x20-v1.json",
        root / "s3-local-runs/s3-paper1-bipolaron-production-20x20-v1/20260928T150000Z/manifest.json",
    ))
    with source.open(newline="", encoding="utf-8") as handle:
        points = list(csv.DictReader(handle))
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4), sharex=True, sharey=True, constrained_layout=True)
    topology_colors = COLORS
    marker_for_g = {0.9: "o", 1.0: "s", 1.1: "^", 0.8: "D"}
    for ax, coupling in zip(axes, (0.9, 1.0, 1.1)):
        subset = [r for r in points if abs(float(r["coupling_scale"]) - coupling) < 1e-10]
        for row in subset:
            classification = row["classification"]
            marginal = classification.startswith("marginal_")
            topology = classification.removeprefix("marginal_")
            color = topology_colors.get(topology, topology_colors["mixed"])
            ax.scatter(
                float(row["V1_eV"]) * 1000.0,
                float(row["U_eV"]),
                marker=marker_for_g[coupling],
                s=75,
                facecolors="none" if marginal else color,
                edgecolors=color,
                linewidths=1.6,
            )
        ax.set_title(f"g = {coupling:.1f}")
        ax.set_xlabel("V₁ (meV)")
        ax.grid(alpha=0.22)
    axes[0].set_ylabel("U (eV)")
    handles = [
        plt.Line2D([0], [0], marker="o", linestyle="", markerfacecolor=c, markeredgecolor=c, label=name)
        for name, c in topology_colors.items()
    ]
    handles += [plt.Line2D([0], [0], marker="o", linestyle="", markerfacecolor="none", markeredgecolor="#333333", label="marginal (<5 meV)")]
    fig.legend(handles=handles, loc="outside lower center", ncol=6, frameon=False)
    fig.suptitle(
        "Bipolaron topology in the frozen 20×20 U–V₁ map\n"
        "g = 0.9–1.1 facets; single g = 0.8 separated control omitted",
        fontsize=14,
        weight="bold",
    )
    return save_figure(fig, output / "figure-3-bipolaron-phase-map", "Bipolaron 20x20 U-V1 model trend")


def figure_4(root: Path, output: Path, inputs: list[Path]):
    data_dir = root / "paper1-local-data/bipolaron-spatial-controls-20261008-85a696c"
    manifest = data_dir / "manifest.json"
    inputs.extend((manifest, root / "configs/s4-paper1-bipolaron-spatial-controls-v1.json"))
    record = json.loads(manifest.read_text(encoding="utf-8"))
    states = record["states"]
    fig, axes = plt.subplots(4, 2, figsize=(9, 15), constrained_layout=True)
    for row, state in enumerate(states):
        path = data_dir / state["npz_path"]
        inputs.append(path)
        with np.load(path, allow_pickle=False) as arrays:
            classification = state["source_point_classification"].replace("_", " ")
            title = f"{state['id']} — {classification}"
            image_panel(axes[row, 0], arrays["lattice_u_A"], f"{title}: u", "coolwarm", center_zero=True, cbar_label="Å")
            image_panel(axes[row, 1], arrays["pair_relative_probability"], f"{title}: pair separation", "magma", cbar_label="probability")
    fig.suptitle("Representative relaxed bipolaron states at 20×20", fontsize=16, weight="bold")
    return save_figure(fig, output / "figure-4-bipolaron-spatial-states", "Bipolaron lattice and pair-density examples")


def figure_5(root: Path, output: Path, inputs: list[Path]):
    data_dir = root / "paper1-local-data/validation-controls/generic-exciton-10x10-20261008-7ce26e7"
    manifest = data_dir / "manifest.json"
    inputs.extend((manifest, root / "configs/s4-paper1-reference-controls-v1.json"))
    record = json.loads(manifest.read_text(encoding="utf-8"))
    branches = record["exciton_branches"]
    fig, axes = plt.subplots(1, len(branches), figsize=(15, 4.4), constrained_layout=True)
    for ax, branch in zip(axes, branches):
        path = data_dir / branch["npz_path"]
        inputs.append(path)
        with np.load(path, allow_pickle=False) as arrays:
            density = relative_exciton_density(arrays["pair_probability"])
            seed_label = branch["initialization"].replace("_", "-")
            image_panel(ax, density, f"{seed_label} seed\nP₀={branch['onsite_probability']:.2f}", "magma", cbar_label="relative probability")
    fig.suptitle("Spin-blind electron–hole validation control (10×10)", fontsize=15, weight="bold")
    fig.text(0.5, 0.015, "10×10 metastable control; seeds denote initial conditions and the model is spin blind.", ha="center", fontsize=9)
    return save_figure(fig, output / "figure-5-spin-blind-exciton-control", "Spin-blind electron-hole control states")


def figure_6(root: Path, output: Path, inputs: list[Path]):
    artifact_root = root / "s1r-local-runs/20260926T-s1r-root-manifold-36260401478/artifacts"
    selected = [
        ("Singlet", next(artifact_root.rglob("s1r-singlet-rprop-onsite-root8.json"))),
        ("Triplet", next(artifact_root.rglob("s1r-triplet-rprop-onsite-root0.json"))),
    ]
    inputs.extend((
        root / "s1r-local-runs/20260926T-s1r-root-manifold-36260401478/artifact_manifest.json",
        root / "s1r-local-runs/20260926T-s1r-root-manifold-36260401478/artifacts/s1r-aggregate-36260401478-1/s1r-aggregate.md",
    ))
    fig, axes = plt.subplots(2, 4, figsize=(12, 6.8), constrained_layout=True)
    energies = {}
    for row, (spin, json_path) in enumerate(selected):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        npz_path = json_path.with_suffix(".npz")
        inputs.extend((json_path, npz_path))
        energies[spin] = float(data["total_referenced_energy_eV"])
        with np.load(npz_path, allow_pickle=False) as arrays:
            image_panel(axes[row, 0], arrays["excitation_density"], f"{spin}: excitation density", "coolwarm", center_zero=True)
            image_panel(axes[row, 1], arrays["lattice_u_A"], f"{spin}: u", "coolwarm", center_zero=True, cbar_label="Å")
            image_panel(axes[row, 2], arrays["lattice_vx_A"], f"{spin}: vₓ", "coolwarm", center_zero=True, cbar_label="Å")
            image_panel(axes[row, 3], arrays["lattice_vy_A"], f"{spin}: vᵧ", "coolwarm", center_zero=True, cbar_label="Å")
    splitting_mev = (energies["Singlet"] - energies["Triplet"]) * 1000.0
    fig.suptitle(
        "Spin-adapted 4×4 validation control — deterministic root promotion\n"
        f"Eₛ − Eₜ = {splitting_mev:.6g} meV (near-degenerate at this control minimum)",
        fontsize=14,
        weight="bold",
    )
    return save_figure(fig, output / "figure-6-spin-adapted-control", "Spin-adapted singlet-triplet validation control")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("figures/paper1"))
    args = parser.parse_args()
    root = args.data_root.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "svg.hashsalt": "holstein-peierls-paper1-s4",
        "savefig.facecolor": "white",
    })

    inputs: list[Path] = []
    results = []
    results.extend(figure_1(output))
    for function in (figure_2, figure_3, figure_4, figure_5, figure_6):
        results.extend(function(root, output, inputs))
    script_path = Path(__file__).resolve()
    manifest = {
        "schema_version": 1,
        "dataset_id": "paper1-static-figure-set-v1",
        "source_commit": git_commit(root),
        "source_script": str(script_path),
        "source_script_sha256": sha256(script_path),
        "python": sys.version.split()[0],
        "matplotlib": matplotlib.__version__,
        "numpy": np.__version__,
        "platform": platform.platform(),
        "thread_environment": {
            key: os.environ.get(key)
            for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")
        },
        "rendering_config_sha256": sha256(root / "pyproject.toml"),
        "input_files": [
            {"path": str(path.relative_to(root)) if path.is_relative_to(root) else str(path), "sha256": sha256(path)}
            for path in sorted(set(inputs + [root / "pyproject.toml"]))
        ],
        "output_files": results,
        "interpretation": {
            "figure_2": "one-polaron generic validation control",
            "figure_3": "S3 model trend; marginal states use open markers under the 5 meV rule",
            "figure_4": "representative S3 states, including a marginal diagonal state",
            "figure_5": "spin-blind e-h validation control; no S/T labels",
            "figure_6": "spin-adapted S1R validation control, not a material prediction",
        },
    }
    manifest_path = output / "figure_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(output), "figure_files": len(results), "manifest": str(manifest_path)}, indent=2))


if __name__ == "__main__":
    main()
