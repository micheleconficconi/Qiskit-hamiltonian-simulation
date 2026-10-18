import argparse
from qiskit_ibm_runtime import QiskitRuntimeService

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-id", type=str, required=True, help="The IBM Quantum Job ID to fetch")
    args = parser.parse_args()

    print("Authenticating...")
    service = QiskitRuntimeService(channel="ibm_quantum_platform")
    
    job = service.job(args.job_id)
    print(f"Backend Used: {job.backend().name}")
    print(f"Job Status:   {job.status()}")
    print(f"Job Status: {job.status()}")
    
    if job.in_final_state():
        if job.status() == "DONE":
            result = job.result()[0]
            print("\n--- Hardware Results ---")
            print(f"Hardware Energy: {result.data.evs:.6f}")
            print(f"Standard Error:  {result.data.stds:.6f}")
        else:
            print(f"Job failed or was cancelled. Error message: {job.error_message()}")
    else:
        print("Job is still running or in queue. Check back later.")

if __name__ == "__main__":
    main()