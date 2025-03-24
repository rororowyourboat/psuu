#!/usr/bin/env python
"""
Quick Optimize Example

This example demonstrates the use of the quick_optimize function,
which provides a simple one-line interface for parameter optimization.
"""

from psuu import quick_optimize


def main():
    """Run a quick optimization experiment."""
    print("PSUU - Quick Optimize Example")
    print("=============================")
    
    # Define a mock simulation command
    # In a real scenario, this would be your actual simulation command
    # Here we're using the Python -c option to create a simple simulation on the fly
    command = """python -c "
import sys, json, random
import numpy as np
import pandas as pd

# Get parameters from command line
beta = float(sys.argv[1].split('=')[1])
gamma = float(sys.argv[2].split('=')[1])

# Simple SIR simulation
N = 1000
I0 = 10
S0 = N - I0
R0 = 0

S, I, R = S0, I0, R0
timesteps = 100
results = []

for t in range(timesteps):
    # Add some randomness to make it interesting
    noise = random.uniform(0.9, 1.1)
    
    # SIR model equations
    new_infections = beta * S * I / N * noise
    new_recoveries = gamma * I * noise
    
    S = S - new_infections
    I = I + new_infections - new_recoveries
    R = R + new_recoveries
    
    results.append({
        'timestep': t,
        'S': S,
        'I': I,
        'R': R
    })

# Output as CSV to stdout
df = pd.DataFrame(results)
print(df.to_csv(index=False))
" --{name}={value}"""
    
    # Run quick optimization
    results = quick_optimize(
        command=command,
        params={"beta": (0.1, 0.5), "gamma": (0.01, 0.1)},
        kpi_column="I",      # Column to optimize
        objective="min",     # Minimize the value
        iterations=10        # Number of iterations to run
    )
    
    # Display results
    print("\nOptimization Results:")
    print(f"Best parameters: beta={results.best_parameters['beta']:.4f}, gamma={results.best_parameters['gamma']:.4f}")
    print(f"Minimum peak infections: {results.best_kpis['objective']:.2f}")
    
    # Show all evaluated parameters and results
    print("\nAll evaluations:")
    pd.set_option('display.max_rows', None)
    print(results.all_results[['param_beta', 'param_gamma', 'kpi_objective']])


if __name__ == "__main__":
    main()
