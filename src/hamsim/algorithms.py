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
        
    qc = synthesis.synthesize(evo_gate)
    return qc