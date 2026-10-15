import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from qiskit.quantum_info import Operator

from hamsim.algorithms import get_qdrift_circuit, get_trotter_circuit
from hamsim.exact import exact_evolution_unitary
from hamsim.models import get_tfim_hamiltonian


def calc_error(H, t, steps, order):
    """Calculates the spectral norm error of the Trotter approximation"""
    exact_U = exact_evolution_unitary(H, t)
    qc = get_trotter_circuit(H, t, steps, order)
    approx_U = Operator(qc).data
    return np.linalg.norm(exact_U - approx_U, ord=2)


def calc_qdrift_error(H, t, steps, seed=42):
    """Calculates the spectral norm error of the qDRIFT approximation"""
    exact_U = exact_evolution_unitary(H, t)
    qc = get_qdrift_circuit(H, t, steps, seed)
    approx_U = Operator(qc).data
    return np.linalg.norm(exact_U - approx_U, ord=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    print(f"Starting Hamiltonian Simulation Benchmark: {config['model']['name']}")

    H = get_tfim_hamiltonian(
        num_qubits=config["model"]["num_qubits"], J=config["model"]["J"], h=config["model"]["h"]
    )

    t = config["simulation"]["time"]
    steps_range = range(
        2, config["simulation"]["max_steps"] + 1, config["simulation"]["step_interval"]
    )

    results = []
    for steps in steps_range:
        err_1 = calc_error(H, t, steps, order=1)
        err_2 = calc_error(H, t, steps, order=2)
        err_qdrift = calc_qdrift_error(H, t, steps, seed=42)

        results.append(
            {
                "steps": steps,
                "trotter_order_1_error": err_1,
                "suzuki_order_2_error": err_2,
                "qdrift_error": err_qdrift,
            }
        )
        print(
            f"Steps: {steps:02d} | 1st Order: {err_1:.4f} | 2nd Order: {err_2:.4f} | qDRIFT: {err_qdrift:.4f}"
        )

    df = pd.DataFrame(results)
    out_path = Path("results") / config["output"]["filename"]
    out_path.parent.mkdir(exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\nData successfully saved to {out_path}")


if __name__ == "__main__":
    main()
