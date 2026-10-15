from hamsim.exact import exact_ground_state_energy
from hamsim.models import get_tfim_hamiltonian
from hamsim.vqe import get_vqe_ansatz, run_vqe_simulation


def test_vqe_convergence():
    """Verify that VQE converges to an energy close to the exact ground state"""
    H = get_tfim_hamiltonian(num_qubits=3, J=1.0, h=0.7)
    exact_energy = exact_ground_state_energy(H)

    ansatz = get_vqe_ansatz(num_qubits=3, reps=1)
    vqe_energy, _, _ = run_vqe_simulation(H, ansatz, maxiter=50, seed=42)

    assert vqe_energy < 0, "VQE failed to minimize the energy below zero."
    assert vqe_energy >= exact_energy - 1e-5, (
        "VQE energy cannot be lower than the exact ground state."
    )
