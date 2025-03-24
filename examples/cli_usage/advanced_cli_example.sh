#!/bin/bash
# Advanced CLI Example for PSUU package
# This example shows how to set up a more complex optimization scenario with custom KPIs

# Ensure we're in the right directory
cd "$(dirname "$0")"
mkdir -p advanced_example
cd advanced_example

# Initialize configuration
echo "Initializing PSUU configuration..."
psuu init

# Add more complex parameter configurations
echo "Adding parameters..."
psuu add-param --name "beta" --range 0.1 0.5
psuu add-param --name "gamma" --range 0.01 0.1
psuu add-param --name "initial_infected" --values 5 10 20 50
psuu add-param --name "quarantine_threshold" --range 50 200
psuu add-param --name "social_distance_factor" --range 0.5 0.9

# Add KPIs - mix of simple and custom
echo "Adding KPIs..."
psuu add-kpi --name "peak" --column "I" --operation "max"
psuu add-kpi --name "total" --column "R" --operation "max"
psuu add-kpi --name "duration" --custom --module "../create_custom_kpi" --function "epidemic_duration"
psuu add-kpi --name "peak_timing" --custom --module "../create_custom_kpi" --function "peak_timing"

# Configure a more advanced optimizer - Bayesian optimization
echo "Configuring Bayesian optimizer..."
psuu set-optimizer --method "bayesian" --objective "peak" --minimize --iterations 30 --n-initial-points 10

# Configure simulation command - here we're using a hypothetical advanced SIR model
# In a real example, this would be your actual simulation script
echo "Updating simulation command..."
cat > advanced_sir_model.py << 'EOF'
#!/usr/bin/env python
"""
Advanced SIR Model with interventions.

This script simulates an SIR epidemic model with additional features:
- Quarantine when infections reach a threshold
- Social distancing effects
- Stochastic transmission

Usage:
    python advanced_sir_model.py --beta=0.3 --gamma=0.1 --initial_infected=10 --quarantine_threshold=100 --social_distance_factor=0.7
"""

import sys
import argparse
import pandas as pd
import numpy as np
import json

def parse_args():
    parser = argparse.ArgumentParser(description='Advanced SIR Model')
    parser.add_argument('--beta', type=float, default=0.3, help='Transmission rate')
    parser.add_argument('--gamma', type=float, default=0.1, help='Recovery rate')
    parser.add_argument('--initial_infected', type=int, default=10, help='Initial infected')
    parser.add_argument('--quarantine_threshold', type=float, default=100, help='Infections to trigger quarantine')
    parser.add_argument('--social_distance_factor', type=float, default=0.7, help='Effect of social distancing')
    return parser.parse_args()

def run_simulation(args):
    # Simulation parameters
    beta = args.beta
    gamma = args.gamma
    initial_infected = args.initial_infected
    quarantine_threshold = args.quarantine_threshold
    social_distance_factor = args.social_distance_factor
    
    # Population parameters
    N = 10000
    I0 = initial_infected
    S0 = N - I0
    R0 = 0
    
    # Initialize
    S, I, R = S0, I0, R0
    timesteps = 200
    quarantine_active = False
    results = []
    
    # Run simulation
    for t in range(timesteps):
        # Check if quarantine should be activated
        if I >= quarantine_threshold and not quarantine_active:
            quarantine_active = True
        
        # Apply social distancing effect if quarantine is active
        effective_beta = beta
        if quarantine_active:
            effective_beta *= social_distance_factor
        
        # Add stochasticity
        stochastic_factor = np.random.normal(1.0, 0.1)
        
        # SIR model equations with stochasticity
        new_infections = effective_beta * S * I / N * stochastic_factor
        new_recoveries = gamma * I * stochastic_factor
        
        S = max(0, S - new_infections)
        I = max(0, I + new_infections - new_recoveries)
        R = R + new_recoveries
        
        # Store results
        results.append({
            'timestep': t,
            'S': S,
            'I': I,
            'R': R,
            'quarantine_active': int(quarantine_active)
        })
        
        # Early stopping if epidemic ends
        if I < 1:
            # Fill in remaining timesteps with final values
            for remaining_t in range(t+1, timesteps):
                results.append({
                    'timestep': remaining_t,
                    'S': S,
                    'I': 0,
                    'R': R,
                    'quarantine_active': int(quarantine_active)
                })
            break
    
    return pd.DataFrame(results)

if __name__ == '__main__':
    args = parse_args()
    df = run_simulation(args)
    
    # Output as CSV to stdout
    print(df.to_csv(index=False))
EOF

chmod +x advanced_sir_model.py

# Update the simulation command in the config
sed -i 's|command: python -m model|command: python ./advanced_sir_model.py|g' psuu_config.yaml

# Set output file to None to use stdout
sed -i 's|output_file: results.csv|output_file: null|g' psuu_config.yaml

echo "Configuration complete! Running optimization..."
psuu run --output "advanced_sir_optimization"

echo "Done! Results should be in advanced_sir_optimization_*.csv/json/yaml files."
