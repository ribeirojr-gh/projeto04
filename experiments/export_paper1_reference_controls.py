"""Export frozen one-polaron and spin-blind exciton validation controls.

This utility creates machine-readable JSON/NPZ products for figure-source
auditing. Its default parameterization is the generic numerical control in
``docs/static-exciton-validation-results.md``; it is not a material fit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np
import scipy

from holstein_peierls.exciton import (
    DEFAULT_EXCITON_BRANCHES,
    ExcitonParameters,
    binding_energy,
    exciton_observables,
    relax_static_exciton,
)
from holstein_peierls.parameters import StaticPolaronParameters
from holstein_peierls.polaron import solve_static_polaron


def _center_position(nx: int, ny: int) -> int:
    return (ny // 2) * nx + (nx // 2) + 1


def _polaron_parameters(
    size: int, max_iterations: int, model: dict[str, object]
) -> StaticPolaronParameters:
    return StaticPolaronParameters(
        nx=size,
        ny=size,
        k1=float(model["K1_eV_per_A2"]),
        k2=float(model["K2_eV_per_A2"]),
        j0x=float(model["Jx_eV"]),
        j0y=float(model["Jy_eV"]),
        alpha_intra=float(model["alpha_intra_eV_per_A"]),
        alpha_interx=float(model["alpha_interx_eV_per_A"]),
        alpha_intery=float(model["alpha_intery_eV_per_A"]),
        polaron_position=_center_position(size, size),
        max_iterations=max_iterations,
        convergence_criterion=1.0e-8,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--config", type=Path,
        default=Path("configs/s4-paper1-reference-controls-v1.json"),
    )
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    sizes = tuple(int(value) for value in config["polaron_sizes"])
    exciton_size = int(config["exciton_size"])
    max_iterations = int(config["numerical"]["max_iterations"])
    model = config["model"]
    initializations = tuple(config["exciton_initializations"])
    if set(initializations) != set(DEFAULT_EXCITON_BRANCHES):
        parser.error("config exciton_initializations must match the solver branches")
    if exciton_size < 3 or any(size < 3 for size in sizes):
        parser.error("all lattice sizes must be at least 3")
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    metadata: dict[str, object] = {
        "schema_version": 1,
        "dataset_id": config["dataset_id"],
        "data_role": "validation_control",
        "model_status": "generic_reference_control_not_material_fit",
        "source_config": str(config_path),
        "source_config_sha256": _sha256(config_path),
        "source_commit": _git_commit(),
        "source_script": str(Path(__file__).resolve()),
        "source_script_sha256": _sha256(Path(__file__).resolve()),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "thread_environment": {
            key: os.environ.get(key)
            for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")
        },
        "parameters": {
            **model,
            "onsite_eh_attraction_eV": config["onsite_eh_attraction_eV"],
            "boundary_conditions": "periodic",
            "optimizer": "legacy-compatible component-wise RPROP with strict convergence",
            "max_iterations": max_iterations,
        },
        "polaron_sizes": list(sizes),
        "exciton_size": exciton_size,
        "exciton_initializations": list(initializations),
        "files": [],
    }

    polarons: dict[int, object] = {}
    for size in sizes:
        parameters = _polaron_parameters(size, max_iterations, model)
        result = solve_static_polaron(
            parameters,
            solver="sparse",
            gradient_mode="optimized",
            legacy_convergence=False,
        )
        if not result.diagnostics.converged_u or not result.diagnostics.converged_vx or not result.diagnostics.converged_vy:
            raise RuntimeError(f"strict polaron convergence failed at {size}x{size}")
        polarons[size] = result
        tag = f"polaron-{size}x{size}"
        array_path = out / f"{tag}.npz"
        np.savez_compressed(
            array_path,
            charge_density=result.charge_density,
            lattice_u_A=result.state.u,
            lattice_vx_A=result.state.vx,
            lattice_vy_A=result.state.vy,
        )
        metadata["files"].append({
            "path": array_path.name,
            "sha256": _sha256(array_path),
            "size_bytes": array_path.stat().st_size,
            "kind": "one_polaron_static_fields",
            "lattice_size": [size, size],
            "total_energy_eV": result.total_energy,
            "formation_energy_eV": result.formation_energy,
            "ipr": result.ipr,
            "iterations": result.diagnostics.iterations,
            "strictly_converged": True,
        })
        print(f"polaron {size}x{size}: E={result.total_energy:.12f} eV IPR={result.ipr:.8f}", flush=True)

    size = exciton_size
    polaron_parameters = _polaron_parameters(size, max_iterations, model)
    parameters = ExcitonParameters.from_reference_polaron(
        polaron_parameters,
        onsite_attraction=float(config["onsite_eh_attraction_eV"]),
    )
    polaron_reference = polarons.get(size)
    if polaron_reference is None:
        polaron_reference = solve_static_polaron(
            polaron_parameters,
            solver="sparse",
            gradient_mode="optimized",
            legacy_convergence=False,
        )
        if not all((polaron_reference.diagnostics.converged_u,
                    polaron_reference.diagnostics.converged_vx,
                    polaron_reference.diagnostics.converged_vy)):
            raise RuntimeError("strict polaron reference convergence failed")

    branch_records = []
    for mode in initializations:
        result = relax_static_exciton(parameters, initialization=mode)
        if not result.diagnostics.converged:
            raise RuntimeError(f"strict exciton convergence failed for {mode}")
        observables = exciton_observables(result.ground_state, parameters)
        tag = f"exciton-{size}x{size}-{mode}"
        array_path = out / f"{tag}.npz"
        np.savez_compressed(
            array_path,
            wavefunction=result.ground_state.wavefunction,
            pair_probability=result.ground_state.probability.reshape(
                size, size, size, size
            ),
            electron_density=result.ground_state.electron_density.reshape(size, size),
            hole_density=result.ground_state.hole_density.reshape(size, size),
            electron_rdm=result.ground_state.electron_density_matrix,
            hole_rdm=result.ground_state.hole_density_matrix,
            lattice_u_A=result.lattice.u,
            lattice_vx_A=result.lattice.vx,
            lattice_vy_A=result.lattice.vy,
        )
        record = {
            "initialization": mode,
            "strictly_converged": True,
            "iterations": result.diagnostics.iterations,
            "final_max_update_A": result.diagnostics.final_max_update,
            "final_max_gradient_eV_per_A": result.diagnostics.final_max_gradient,
            "electronic_energy_eV": result.energy.electronic,
            "lattice_energy_eV": result.energy.lattice,
            "total_energy_eV": result.energy.total,
            "binding_energy_eV": binding_energy(
                result.energy.total,
                polaron_reference.total_energy,
                polaron_reference.total_energy,
            ),
            "onsite_probability": observables.onsite_probability,
            "electron_ipr": observables.electron_ipr,
            "hole_ipr": observables.hole_ipr,
            "mean_eh_separation_sites": observables.mean_separation_sites,
            "rms_eh_separation_sites": observables.rms_separation_sites,
            "npz_path": array_path.name,
            "npz_sha256": _sha256(array_path),
        }
        branch_records.append(record)
        print(
            f"exciton {mode:10s}: E={result.energy.total:.12f} eV "
            f"P0={observables.onsite_probability:.6f} "
            f"<r>={observables.mean_separation_sites:.6f} sites",
            flush=True,
        )

    metadata["exciton_branches"] = branch_records
    metadata["dissociation_reference_eV"] = 2.0 * polaron_reference.total_energy
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    metadata["manifest_sha256"] = _sha256(manifest_path)
    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {summary_path}", flush=True)


if __name__ == "__main__":
    main()
