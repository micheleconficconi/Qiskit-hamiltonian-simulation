import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Load the benchmark data
    data_path = "results/benchmark_tfim.csv"
    df = pd.read_csv(data_path)
    
    # Configure the plot style
    plt.figure(figsize=(8, 5))
    
    # Plot both error curves
    plt.plot(df['steps'], df['trotter_order_1_error'], 
             marker='o', linestyle='-', linewidth=2, label='1st Order (Lie-Trotter)')
    plt.plot(df['steps'], df['suzuki_order_2_error'], 
             marker='s', linestyle='-', linewidth=2, label='2nd Order (Suzuki-Trotter)')
    
    # Use log-log scale to clearly show the difference in asymptotic scaling
    plt.xscale('log')
    plt.yscale('log')
    
    # Formatting
    plt.xlabel('Number of Trotter Steps (r)', fontsize=12)
    plt.ylabel('Spectral Norm Error $||U_{exact} - U_{approx}||_2$', fontsize=12)
    plt.title('Hamiltonian Simulation Convergence (4-Qubit TFIM)', fontsize=14)
    plt.grid(True, which="both", linestyle="--", alpha=0.6)
    plt.legend(fontsize=11)
    
    # Save the figure
    out_file = "results/tfim_scaling.png"
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    print(f"Convergence plot saved to {out_file}")

if __name__ == "__main__":
    main()