#!/bin/bash
# Example of using PSUU's CLI interface

# Ensure we're in the right directory
cd "$(dirname "$0")"
mkdir -p cli_example
cd cli_example

# Initialize configuration
psuu init

# Add parameters
psuu add-param --name "beta" --range 0.1 0.5
psuu add-param --name "gamma" --range 0.01 0.1
psuu add-param --name "population" --values 1000 5000 10000

# Add KPIs
psuu add-kpi --name "peak" --column "I" --operation "max"
psuu add-kpi --name "total" --column "S" --operation "min"
psuu add-kpi --name "duration" --custom --module "custom_kpis" --function "epidemic_duration"

# Create a simple Python file with custom KPI function
cat > custom_kpis.py << 'EOF'
def epidemic_duration(df, threshold=1):
    """Calculate epidemic duration KPI."""
    # Find time from first to last infection above threshold
    above_threshold = df[df["I"] > threshold]
    if len(above_threshold) == 0:
        return 0
    return above_threshold.iloc[-1]["time"] - above_threshold.iloc[0]["time"]
EOF

# Configure optimizer for minimizing peak infections
psuu set-optimizer --method "random" --objective "peak" --minimize --iterations 20

# Configure simulation command (update with actual command for your environment)
# This example assumes the cadcad-sir command is available
echo "Updating simulation command..."
sed -i 's|command: python -m model|command: cadcad-sir|g' psuu_config.yaml

# Run optimization
echo "Running optimization..."
psuu run --output "sir_results"

echo "Done! Results should be in sir_results_*.csv/json/yaml files."
