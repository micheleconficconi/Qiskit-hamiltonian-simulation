from pathlib import Path

import pandas as pd
import numpy as np

from hamsim.exact import exact_ground_state_energy
from hamsim.models import get_tfim_hamiltonian
from hamsim.vqe import get_vqe_ansatz, run_vqe_simulation


def main():
    print("Starting Hybrid Quantum-Classical VQE benchmark")

    num_qubits = 4
    H = get_tfim_hamiltonian(num_qubits, J=1.0, h=0.7)

    exact_energy = exact_ground_state_energy(H)
    print(f"Exact Ground State Energy: {exact_energy:.6f}")

    ansatz = get_vqe_ansatz(num_qubits, reps=2)
    print(f"Ansatz initialized with {ansatz.num_parameters} optimizable parameters.")

    vqe_energy, optimal_params, history = run_vqe_simulation(H, ansatz, maxiter=150)
    print(f"VQE Optimized Energy:      {vqe_energy:.6f}")
    print(f"Energy Error (Delta):      {abs(exact_energy - vqe_energy):.6f}")

    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    np.save(out_dir / "vqe_optimal_params.npy", optimal_params)    
    print(f"VQE Optimized Energy:      {vqe_energy:.6f}")
    print(f"Energy Error (Delta):      {abs(exact_energy - vqe_energy):.6f}")

    results = [
        {"iteration": i, "vqe_energy": E, "exact_energy": exact_energy}
        for i, E in enumerate(history)
    ]

    df = pd.DataFrame(results)
    out_path = Path("results") / "vqe_optimization_history.csv"
    out_path.parent.mkdir(exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\nOptimization trajectory saved to {out_path}")


if __name__ == "__main__":
    main()
