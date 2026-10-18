import argparse
import json
from pathlib import Path

from qiskit_ibm_runtime import QiskitRuntimeService


def main():
    parser = argparse.ArgumentParser(description="Fetch IBM Quantum hardware job results")
    parser.add_argument("--job-id", type=str, required=True, help="The IBM Quantum Job ID to fetch")
    args = parser.parse_args()

    local_matches = list(Path("results").glob(f"hardware_*_{args.job_id}.json"))
    if local_matches:
        with open(local_matches[0], "r") as f:
            data = json.load(f)
        print(f"Loaded post-processed results from {local_matches[0]}:")
        print(f"Mode:            {data['mode']}")
        print(f"Backend Used:    {data['backend']}")
        print(f"Circuit Depth:   {data['depth']} | Ops: {data['ops']}")
        print(f"Ideal Energy:    {data['ideal_energy']:.6f}")
        print(f"Hardware Energy: {data['hardware_energy']:.6f}")
        print(f"Standard Error:  {data['standard_error']:.6f}")
        return

    print("Authenticating...")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", instance="auto")

    job = service.job(args.job_id)
    print(f"Backend Used: {job.backend().name}")
    print(f"Job Status:   {job.status()}")

    if job.in_final_state():
        if job.status() == "DONE":
            result = job.result()[0]
            if hasattr(result, "data") and hasattr(result.data, "evs"):
                print("Hardware Results")
                print(f"Hardware Energy: {float(result.data.evs):.6f}")
                print(f"Standard Error:  {float(result.data.stds):.6f}")
            else:
                print(
                    "Note: This job was executed with the client-side executor_estimator "
                    "(QuantumProgramResult). Check the terminal output or JSON file from run_hardware.py."
                )
        else:
            print(f"Job failed or was cancelled. Error message: {job.error_message()}")
    else:
        print("Job is still running or in queue. Check back later.")


if __name__ == "__main__":
    main()
