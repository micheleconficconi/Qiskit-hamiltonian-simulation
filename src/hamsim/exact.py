import numpy as np
import scipy.linalg
from qiskit.quantum_info import SparsePauliOp


def exact_evolution_unitary(hamiltonian: SparsePauliOp, time: float) -> np.ndarray:
    """
    Computes the exact time evolution unitary U(t) = exp(-iHt).
    """
    h_matrix = hamiltonian.to_matrix()

    return scipy.linalg.expm(-1j * h_matrix * time)
