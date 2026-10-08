"""Export spatial fields for selected states already present in the S3 map."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy

from holstein_peierls.parameters import StaticPolaronParameters
from holstein_peierls.s3_campaign import expand_tasks, task_id
from holstein_peierls.two_particle.observables import pair_observables
from holstein_peierls.two_particle.parameters import BipolaronParameters
from bipolaron_branch_benchmark_seeded import (
    distortion_ratios,
    relax_seeded,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_value(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    source_run = args.source_run
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_manifest_path = Path(manifest["source_campaign_manifest"])
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    source_tasks = expand_tasks(source_manifest)
    source_points_path = source_run / "points.csv"
    with source_points_path.open(newline="", encoding="utf-8") as handle:
        source_points = list(csv.DictReader(handle))
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    provenance = {
        "schema_version": 1,
        "dataset_id": manifest["dataset_id"],
        "data_role": manifest["data_role"],
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": git_value("rev-parse", "HEAD"),
        "source_branch": git_value("branch", "--show-current"),
        "git_status": git_value("status", "--short"),
        "source_script": str(Path(__file__).resolve()),
        "source_script_sha256": sha256(Path(__file__).resolve()),
        "manifest_path": str(manifest_path),
        "manifest_sha256": sha256(manifest_path),
        "source_campaign_manifest_sha256": sha256(source_manifest_path),
        "source_run": str(source_run),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "thread_environment": {
            name: os.environ.get(name)
            for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")
        },
        "states": [],
    }

    model = manifest["model"]
    numerical = manifest["numerical"]
    for state in manifest["states"]:
        size = int(manifest["lattice_size"][0])
        coupling = float(state["coupling_scale"])
        alpha_intra = float(model["base_alpha_intra_eV_per_A"]) * coupling
        alpha_x = float(model["base_alpha_x_eV_per_A"]) * coupling
        alpha_y = float(model["base_alpha_y_eV_per_A"]) * coupling
        single = StaticPolaronParameters(
            nx=size,
            ny=size,
            polaron_position=(size // 2) * size + (size // 2) + 1,
            k1=float(model["K1_eV_per_A2"]),
            k2=float(model["K2_eV_per_A2"]),
            j0x=float(model["Jx_eV"]),
            j0y=float(model["Jy_eV"]),
            alpha_intra=alpha_intra,
            alpha_interx=alpha_x,
            alpha_intery=alpha_y,
            max_iterations=int(numerical["max_iterations"]),
            convergence_criterion=float(numerical["coordinate_update_tolerance_A"]),
        )
        parameters = BipolaronParameters.from_polaron_parameters(
            single,
            hubbard_u=float(state["U_eV"]),
            nearest_neighbor_v=float(state["V1_eV"]),
        )
        parameters = replace(
            parameters,
            pair_position=single.polaron_position,
            max_iterations=int(numerical["max_iterations"]),
            convergence_criterion=float(numerical["coordinate_update_tolerance_A"]),
            gradient_convergence_criterion=float(numerical["gradient_tolerance_eV_per_A"]),
            eigensolver_tolerance=float(numerical["eigensolver_tolerance"]),
        )

        task_match = next(
            task for task in source_tasks
            if task["size"] == size
            and abs(float(task["coupling_scale"]) - coupling) < 1e-14
            and abs(float(task["U_eV"]) - float(state["U_eV"])) < 1e-14
            and abs(float(task["V1_eV"]) - float(state["V1_eV"])) < 1e-14
            and task["branch"] == state["branch"]
        )
        identifier = task_id(task_match)
        source_result_path = source_run / "branches" / identifier / "branch_result.json"
        source_record = json.loads(source_result_path.read_text(encoding="utf-8"))
        point = next(
            row for row in source_points
            if int(row["size"]) == size
            and abs(float(row["coupling_scale"]) - coupling) < 1e-14
            and abs(float(row["U_eV"]) - float(state["U_eV"])) < 1e-14
            and abs(float(row["V1_eV"]) - float(state["V1_eV"])) < 1e-14
        )
        if point["classification"] != state["expected_observable_classification"]:
            raise RuntimeError(
                f"source point classification mismatch for {state['id']}: "
                f"{point['classification']} != {state['expected_observable_classification']}"
            )

        result = relax_seeded(parameters, branch=state["branch"])
        if not result.diagnostics.converged:
            raise RuntimeError(f"strict convergence failed for state {state['id']}")
        observables = pair_observables(result.ground_state, parameters)
        ratio_x, ratio_y = distortion_ratios(result, parameters)
        probability = result.ground_state.probability
        yy, xx = np.indices((parameters.ny, parameters.nx))
        sy, sx = yy.ravel(), xx.ravel()
        iy, ix = np.repeat(sy, parameters.n_sites), np.repeat(sx, parameters.n_sites)
        jy, jx = np.tile(sy, parameters.n_sites), np.tile(sx, parameters.n_sites)
        dy = (jy - iy) % parameters.ny
        dx = (jx - ix) % parameters.nx
        relative_density = np.bincount(
            dy * parameters.nx + dx,
            weights=probability.ravel(order="C"),
            minlength=parameters.n_sites,
        ).reshape(parameters.ny, parameters.nx)
        diagonal_probability = float(
            relative_density[1, 1]
            + relative_density[1, -1]
            + relative_density[-1, 1]
            + relative_density[-1, -1]
        )

        array_path = out / f"bipolaron-20x20-{state['id']}.npz"
        np.savez_compressed(
            array_path,
            pair_relative_probability=relative_density,
            one_body_density=result.ground_state.site_density.reshape(size, size),
            lattice_u_A=result.u,
            lattice_vx_A=result.vx,
            lattice_vy_A=result.vy,
        )
        energy_difference = float(result.energy.total) - float(source_record["total_energy_eV"])
        if abs(energy_difference) > 1.0e-8:
            raise RuntimeError(
                f"exported {state['id']} energy differs from source by {energy_difference:.3e} eV"
            )
        record = {
            **state,
            "task_id": identifier,
            "source_branch_result": str(source_result_path),
            "source_branch_result_sha256": sha256(source_result_path),
            "source_point_classification": point["classification"],
            "source_point_csv_sha256": sha256(source_points_path),
            "npz_path": array_path.name,
            "npz_sha256": sha256(array_path),
            "total_energy_eV": result.energy.total,
            "source_total_energy_eV": source_record["total_energy_eV"],
            "energy_difference_from_source_eV": energy_difference,
            "strictly_converged": result.diagnostics.converged,
            "iterations": result.diagnostics.iterations,
            "final_max_update_A": result.diagnostics.final_max_update,
            "final_max_gradient_eV_per_A": result.diagnostics.final_max_gradient,
            "P_onsite": observables.onsite_probability,
            "P_nn_x": observables.nearest_neighbour_x_probability,
            "P_nn_y": observables.nearest_neighbour_y_probability,
            "P_diagonal": diagonal_probability,
            "mean_separation_sites": observables.mean_separation,
            "one_body_ipr": observables.one_body_ipr,
            "max_delta_tx_over_Jx": ratio_x,
            "max_delta_ty_over_Jy": ratio_y,
            "linear_peierls_gate": max(ratio_x, ratio_y) <= 0.25,
        }
        provenance["states"].append(record)
        print(
            f"{state['id']}: E={result.energy.total:.12f} eV "
            f"P0={observables.onsite_probability:.5f} "
            f"Pdiag={observables.diagonal_probability:.5f} "
            f"<r>={observables.mean_separation:.5f}",
            flush=True,
        )

    path = out / "manifest.json"
    path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path}", flush=True)


if __name__ == "__main__":
    main()
