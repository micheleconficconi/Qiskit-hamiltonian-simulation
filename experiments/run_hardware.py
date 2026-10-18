import argparse
import json
from pathlib import Path

import numpy as np
from qiskit.primitives import StatevectorEstimator
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime.executor_estimator import Estimator

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
        help="Estimator resilience level (0: none, 1: TREX, 2: ZNE + gate twirling)",
    )
    args = parser.parse_args()

    # Step 1: Map problem to abstract quantum circuit and observable
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

    print("Authenticating with IBM Quantum...")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", instance="auto")

    print("Finding the least busy backend...")
    backend = service.least_busy(simulator=False, operational=True, min_num_qubits=num_qubits)
    print(f"Selected Backend: {backend.name}")

    print("Transpiling circuit for the target physical hardware...")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=3, seed_transpiler=42)
    isa_circuit = pm.run(qc)
    isa_observable = observable.apply_layout(isa_circuit.layout)

    ops_count = dict(isa_circuit.count_ops())
    print(f"ISA Circuit Stats -> Depth: {isa_circuit.depth()} | Total Ops: {ops_count}")

    print(f"Submitting job (mode={args.mode}, resilience_level={args.resilience_level})...")
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
    job_id = job.job_id()
    print(f"Job successfully submitted! Job ID: {job_id}")
    print("Waiting for hardware execution and client-side Estimator post-processing...")

    pub_result = job.result()[0]
    hw_energy = float(pub_result.data.evs)
    hw_std = float(pub_result.data.stds)

    print("Hardware Results:")
    print(f"Mode:            {args.mode}")
    print(f"Backend Used:    {backend.name}")
    print(f"Ideal Energy:    {ideal_energy:.6f}")
    print(f"Hardware Energy: {hw_energy:.6f}")
    print(f"Standard Error:  {hw_std:.6f}")
    print(f"Absolute Gap:    {abs(ideal_energy - hw_energy):.6f}")

    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    summary_path = out_dir / f"hardware_{args.mode}_{job_id}.json"
    with open(summary_path, "w") as f:
        json.dump(
            {
                "job_id": job_id,
                "mode": args.mode,
                "backend": backend.name,
                "resilience_level": args.resilience_level,
                "depth": isa_circuit.depth(),
                "ops": ops_count,
                "ideal_energy": ideal_energy,
                "hardware_energy": hw_energy,
                "standard_error": hw_std,
            },
            f,
            indent=2,
        )
    print(f"Saved hardware result summary to {summary_path}")


if __name__ == "__main__":
    main()
