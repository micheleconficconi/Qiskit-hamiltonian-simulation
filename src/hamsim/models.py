from qiskit.quantum_info import SparsePauliOp


def get_tfim_hamiltonian(num_qubits: int, J: float = 1.0, h: float = 1.0) -> SparsePauliOp:
    """
    Generates the 1D Transverse-Field Ising Model (TFIM) Hamiltonian
    with open boundary conditions.
    """
    op_list = []

    for i in range(num_qubits - 1):
        op_list.append(("ZZ", [i, i + 1], -J))

    for i in range(num_qubits):
        op_list.append(("X", [i], -h))

    return SparsePauliOp.from_sparse_list(op_list, num_qubits=num_qubits)
