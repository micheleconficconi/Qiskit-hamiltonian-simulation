import argparse
from pathlib import Path

import numpy as np
from qiskit.primitives import StatevectorEstimator
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2 as Estimator
from qiskit_ibm_runtime import QiskitRuntimeService

from hamsim.algorithms import get_trotter_circuit
from hamsim.models import get_tfim_hamiltonian
from hamsim.vqe import get_vqe_ansatz


def main():
    parser = argparse.ArgumentParser(description="Run TFIM circuits on IBM Quantum Hardware")
    parser.add_argument(
        "--mode",
        choices=["trotter", "vqe"],
        default="trotter",
        help="Which circuit to evaluate on hardware (default: trotter)",
    )
    parser.add_argument("--steps", type=int, default=2, help="Number of Trotter steps")
    parser.add_argument(
        "--resilience-level",
        type=int,
        default=1,
        choices=[0, 1, 2],
        help="EstimatorV2 resilience level (0: none, 1: TREX, 2: ZNE + gate twirling)",
    )
    args = parser.parse_args()

    num_qubits = 4
    H = get_tfim_hamiltonian(num_qubits, J=1.0, h=0.7)
    observable = H

    if args.mode == "trotter":
        t = 1.0
        qc = get_trotter_circuit(H, t, steps=args.steps, order=1)
        param_values = None
    else:
        qc = get_vqe_ansatz(num_qubits, reps=2)
        params_path = Path("results") / "vqe_optimal_params.npy"
        if not params_path.exists():
            raise FileNotFoundError(
                f"Missing {params_path}. Run `python experiments/run_vqe.py` first."
            )
        param_values = np.load(params_path)

    ideal_estimator = StatevectorEstimator()
    ideal_pub = (qc, observable, param_values) if param_values is not None else (qc, observable)
    ideal_energy = float(ideal_estimator.run([ideal_pub]).result()[0].data.evs)
    print(f"Noiseless Ideal Circuit Energy ({args.mode}): {ideal_energy:.6f}")

    # Step 2: Authenticate & Optimize for target hardware ISA
    print("Authenticating with IBM Quantum...")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", instance="auto")

    print("Finding the least busy backend...")
    backend = service.least_busy(simulator=False, operational=True, min_num_qubits=num_qubits)
    print(f"Selected Backend: {backend.name}")

    print("Transpiling circuit for the target physical hardware...")
    pm = generate_preset_pass_manager(
        backend=backend, optimization_level=3, seed_transpiler=42
    )
    isa_circuit = pm.run(qc)
    isa_observable = observable.apply_layout(isa_circuit.layout)

    print(
        f"ISA Circuit Stats -> Depth: {isa_circuit.depth()} | "
        f"Total Ops: {dict(isa_circuit.count_ops())}"
    )

    print(f"Submitting job (resilience_level={args.resilience_level})...")
    estimator = Estimator(mode=backend)
    estimator.options.resilience_level = args.resilience_level
    estimator.options.dynamical_decoupling.enable = True
    estimator.options.dynamical_decoupling.sequence_type = "XY4"

    pub = (
        (isa_circuit, isa_observable, param_values)
        if param_values is not None
        else (isa_circuit, isa_observable)
    )

    job = estimator.run(pubs=[pub])
    print(f"Job successfully submitted! Job ID: {job.job_id()}")


if __name__ == "__main__":
    main()