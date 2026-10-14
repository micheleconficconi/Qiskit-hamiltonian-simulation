import yaml
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from qiskit.quantum_info import Operator

from hamsim.models import get_tfim_hamiltonian
from hamsim.exact import exact_evolution_unitary
from hamsim.algorithms import get_trotter_circuit

def calc_error(H, t, steps, order):
    """Calculates the spectral norm error of the Trotter approximation."""
    exact_U = exact_evolution_unitary(H, t)
    qc = get_trotter_circuit(H, t, steps, order)
    approx_U = Operator(qc).data
    return np.linalg.norm(exact_U - approx_U, ord=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    args = parser.parse_args()
    
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
        
    print(f"Starting Hamiltonian Simulation Benchmark: {config['model']['name']}")
    
    H = get_tfim_hamiltonian(
        num_qubits=config['model']['num_qubits'],
        J=config['model']['J'],
        h=config['model']['h']
    )
    
    t = config['simulation']['time']
    steps_range = range(2, config['simulation']['max_steps'] + 1, config['simulation']['step_interval'])
    
    results = []
    for steps in steps_range:
        err_1 = calc_error(H, t, steps, order=1)
        err_2 = calc_error(H, t, steps, order=2)
        
        results.append({
            "steps": steps, 
            "trotter_order_1_error": err_1, 
            "suzuki_order_2_error": err_2
        })
        print(f"Steps: {steps:02d} | 1st Order Error: {err_1:.6f} | 2nd Order Error: {err_2:.6f}")
        
    df = pd.DataFrame(results)
    out_path = Path("results") / config['output']['filename']
    out_path.parent.mkdir(exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\nData successfully saved to {out_path}")

if __name__ == "__main__":
    main()