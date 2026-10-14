import numpy as np
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.synthesis import LieTrotter, SuzukiTrotter
from qiskit.quantum_info import SparsePauliOp
from qiskit import QuantumCircuit

def get_trotter_circuit(hamiltonian: SparsePauliOp, time: float, steps: int, order: int = 1) -> QuantumCircuit:
    """
    Constructs the quantum circuit for Hamiltonian simulation using 
    product formulas (First-order Lie-Trotter or higher-order Suzuki-Trotter).
    """
    evo_gate = PauliEvolutionGate(hamiltonian, time=time)
    
    if order == 1:
        synthesis = LieTrotter(reps=steps)
    elif order % 2 == 0:
        synthesis = SuzukiTrotter(order=order, reps=steps)
    else:
        raise ValueError("Suzuki-Trotter order must be an even integer (e.g., 2, 4) or 1 for Lie-Trotter.")
        
    return synthesis.synthesize(evo_gate)

def get_qdrift_circuit(hamiltonian: SparsePauliOp, time: float, steps: int, seed: int = None) -> QuantumCircuit:
    """
    Constructs the quantum circuit for Hamiltonian simulation using the stochastic qDRIFT protocol.
    """
    if seed is not None:
        np.random.seed(seed)
        
    coeffs = hamiltonian.coeffs.real
    abs_coeffs = np.abs(coeffs)
    lambda_norm = np.sum(abs_coeffs)
    probabilities = abs_coeffs / lambda_norm
    
    tau = (lambda_norm * time) / steps
    
    qc = QuantumCircuit(hamiltonian.num_qubits)
    synthesis = LieTrotter() 
    
    sampled_indices = np.random.choice(len(hamiltonian), size=steps, p=probabilities)
    
    for idx in sampled_indices:
        sign = np.sign(coeffs[idx])
        term_op = SparsePauliOp(hamiltonian.paulis[idx], coeffs=[sign])
        evo_gate = PauliEvolutionGate(term_op, time=tau)
        
        qc.compose(synthesis.synthesize(evo_gate), inplace=True)
        
    return qc