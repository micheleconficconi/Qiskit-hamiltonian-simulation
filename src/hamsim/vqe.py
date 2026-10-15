import numpy as np
import scipy.optimize
from qiskit.circuit.library import n_local
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp


def get_vqe_ansatz(num_qubits: int, reps: int = 1):
    """reates a hardware-efficient parameterized quantum circuit (ansatz)"""
    return n_local(
        num_qubits=num_qubits,
        rotation_blocks=["ry"],
        entanglement_blocks="cz",
        reps=reps,
        entanglement="linear",
    )


def run_vqe_simulation(hamiltonian: SparsePauliOp, ansatz, maxiter: int = 200, seed: int = 42):
    """Executes the hybrid quantum-classical VQE loop to find the ground state energy.
    Uses StatevectorEstimator for exact local expectation value calculation"""
    estimator = StatevectorEstimator()
    np.random.seed(seed)

    energy_history = []

    def cost_function(params):
        pub = (ansatz, hamiltonian, params)
        job = estimator.run([pub])
        result = job.result()[0]

        energy = result.data.evs
        energy_history.append(energy)
        return energy

    initial_params = np.random.uniform(-np.pi, np.pi, ansatz.num_parameters)

    result = scipy.optimize.minimize(
        cost_function, initial_params, method="COBYLA", options={"maxiter": maxiter}
    )

    return result.fun, result.x, energy_history
