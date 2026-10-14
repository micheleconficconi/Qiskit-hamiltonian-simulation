import os
import argparse
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as Estimator
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from hamsim.models import get_tfim_hamiltonian
from hamsim.algorithms import get_trotter_circuit

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=2, help="Number of Trotter steps")
    args = parser.parse_args()

    print("Authenticating with IBM Quantum...")
    service = QiskitRuntimeService(channel="ibm_quantum_platform")
    
    print("Finding the least busy backend...")
    backend = service.least_busy(simulator=False, operational=True)
    print(f"Selected Backend: {backend.name}")

    num_qubits = 4
    H = get_tfim_hamiltonian(num_qubits, J=1.0, h=0.7)
    
    observable = H 
    
    t = 1.0
    qc = get_trotter_circuit(H, t, steps=args.steps, order=1)
    
    print("Transpiling circuit for the target physical hardware...")
    pm = generate_preset_pass_manager(target=backend.target, optimization_level=1)
    isa_circuit = pm.run(qc)
    isa_observable = observable.apply_layout(isa_circuit.layout)

    print("Submitting job to the quantum hardware...")
    estimator = Estimator(mode=backend)
    
    pub = (isa_circuit, isa_observable)
    
    job = estimator.run(pubs=[pub])
    print(f"Job successfully submitted! Job ID: {job.job_id()}")
    print("You can monitor the job status on your IBM Quantum Dashboard.")
    

if __name__ == "__main__":
    main()