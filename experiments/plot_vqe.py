import matplotlib.pyplot as plt
import pandas as pd


def main():
    data_path = "results/vqe_optimization_history.csv"
    df = pd.read_csv(data_path)

    plt.figure(figsize=(8, 5))

    plt.plot(
        df["iteration"],
        df["vqe_energy"],
        marker="o",
        markersize=4,
        linestyle="-",
        color="teal",
        label="VQE Energy (COBYLA)",
    )

    exact_energy = df["exact_energy"].iloc[0]
    plt.axhline(
        y=exact_energy,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Exact Energy ({exact_energy:.4f})",
    )

    # Formatting
    plt.xlabel("Optimization Iteration", fontsize=12)
    plt.ylabel("Expectation Value (Energy)", fontsize=12)
    plt.title("VQE Optimization Convergence (4-Qubit TFIM)", fontsize=14)
    plt.grid(True, which="both", linestyle="--", alpha=0.6)
    plt.legend(fontsize=11)

    out_file = "results/vqe_convergence.png"
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    print(f"VQE convergence plot saved to {out_file}")


if __name__ == "__main__":
    main()
