# Hamiltonian Simulation Benchmarks in Qiskit

![CI](https://github.com/micheleconficconi/Qiskit-hamiltonian-simulation/actions/workflows/ci.yml/badge.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A benchmarking suite for evaluating product-formula Hamiltonian simulation algorithms (Lie-Trotter, Suzuki-Trotter) using Qiskit. This repository provides reproducible infrastructure for comparing approximate quantum time-evolution against exact classical baselines, with a focus on convergence scaling and error bounds.

## Benchmark: Transverse-Field Ising Model (TFIM)
The primary validation model is a 1D Transverse-Field Ising Model ($H = -J \sum Z_i Z_{i+1} - h \sum X_i$). The plot below demonstrates the asymptotic scaling difference between first-order and second-order product formulas as the number of time slices ($r$) increases.

![TFIM Scaling Convergence](results/tfim_scaling.png)
*Convergence of spectral norm error $||U_{exact} - U_{approx}||_2$ for a 4-qubit TFIM ($J=1.0$, $h=0.7$, $t=1.0$). First-order Lie-Trotter exhibits $O(1/r)$ scaling, while second-order Suzuki-Trotter achieves $O(1/r^2)$ scaling.*

## Quickstart

This project uses Docker to ensure completely reproducible environments across Linux, macOS, and Windows without polluting your local Python environment.

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- (Optional) An IBM Quantum token for hardware execution

### Running the Environment
Clone the repository and build the container:
```bash
git clone [https://github.com/micheleconficconi/Qiskit-hamiltonian-simulation.git](https://github.com/micheleconficconi/Qiskit-hamiltonian-simulation.git)
cd Qiskit-hamiltonian-simulation
```

**1. Run the test suite:**
```bash
docker compose run --rm bench pytest -v
```

**2. Execute the benchmark sweep (generates CSV data):**
```bash
docker compose run --rm bench python experiments/run_benchmark.py --config experiments/configs/tfim.yaml
```

**3. Generate the convergence plot:**
```bash
docker compose run --rm bench python experiments/plot_benchmark.py
```

**4. Open Jupyter Lab for interactive exploration:**
```bash
docker compose up jupyter
```
*Access the lab via the URL printed in your terminal (usually `http://127.0.0.1:8888`).*

## Repository Structure

```text
.
├── experiments/
│   ├── configs/            # YAML files defining experimental parameters
│   ├── run_benchmark.py    # Main orchestration script
│   └── plot_benchmark.py   # Plotting utilities
├── src/
│   └── hamsim/
│       ├── algorithms.py   # Trotterization circuit synthesis (Qiskit)
│       ├── exact.py        # Classical exact evolution (SciPy)
│       └── models.py       # SparsePauliOp Hamiltonian definitions
├── tests/                  # Pytest verification suite
├── pyproject.toml          # Project metadata and dependencies
└── docker-compose.yml      # Container orchestration
```

## Hardware Execution (IBM Quantum)
To run circuits on actual IBM Quantum hardware, create a `.env` file in the root directory and add your token:
```text
QISKIT_IBM_TOKEN=your_token_here
```
The Docker environment will automatically inject this into Qiskit Runtime sessions.

## License
Distributed under the Apache 2.0 License. See `LICENSE` for more information.
