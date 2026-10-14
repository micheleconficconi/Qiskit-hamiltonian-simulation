import itertools

import numpy as np
from qiskit.quantum_info import Operator

from hamsim.algorithms import get_qdrift_circuit, get_trotter_circuit
from hamsim.exact import exact_evolution_unitary
from hamsim.models import get_tfim_hamiltonian


def trotter_error(H, t, steps, order):
    """Calculates the spectral norm of the difference between exact and approximate evolution."""
    exact_U = exact_evolution_unitary(H, t)
    qc = get_trotter_circuit(H, t, steps, order)
    approx_U = Operator(qc).data
    return np.linalg.norm(exact_U - approx_U, ord=2)


def test_trotter_error_decreases_with_steps():
    """Verify that first-order Trotter error decreases monotonically."""
    H = get_tfim_hamiltonian(num_qubits=4, J=1.0, h=0.7)
    errs = [trotter_error(H, t=1.0, steps=r, order=1) for r in (2, 4, 8, 16)]
    assert all(a > b for a, b in itertools.pairwise(errs)), "Error did not decrease with steps"


def test_suzuki_better_than_trotter():
    """Verify that second-order Suzuki is more accurate than first-order Trotter."""
    H = get_tfim_hamiltonian(num_qubits=4, J=1.0, h=0.7)
    err_1st = trotter_error(H, t=1.0, steps=4, order=1)
    err_2nd = trotter_error(H, t=1.0, steps=4, order=2)
    assert err_2nd < err_1st, "Second-order Suzuki was not more accurate"


def test_qdrift_reproducibility():
    """Verify that qDRIFT circuits are exactly reproducible with a fixed seed."""
    H = get_tfim_hamiltonian(num_qubits=4, J=1.0, h=0.7)

    # Generate two independent circuits using the same seed
    qc1 = get_qdrift_circuit(H, time=1.0, steps=10, seed=42)
    qc2 = get_qdrift_circuit(H, time=1.0, steps=10, seed=42)

    U1 = Operator(qc1).data
    U2 = Operator(qc2).data

    assert np.allclose(U1, U2), "qDRIFT circuits with identical seeds produced different unitaries"
