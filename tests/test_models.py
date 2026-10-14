# RUN: sudo docker compose run --rm bench pytest -q

import numpy as np

from hamsim.exact import exact_evolution_unitary
from hamsim.models import get_tfim_hamiltonian


def test_tfim_hermitian():
    """Verify that the generated Hamiltonian is a Hermitian matrix (H = H^dagger)."""
    H = get_tfim_hamiltonian(num_qubits=4)
    mat = H.to_matrix()

    assert np.allclose(mat, mat.conj().T), "Hamiltonian is not Hermitian"


def test_exact_unitary():
    """Verify that the exact evolution produces a unitary matrix (U @ U^dagger = I)."""
    num_qubits = 3
    H = get_tfim_hamiltonian(num_qubits)
    U = exact_evolution_unitary(H, time=1.0)

    identity = np.eye(2**num_qubits)

    assert np.allclose(U @ U.conj().T, identity), "Evolution operator is not unitary"
