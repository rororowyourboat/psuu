# Ways to Run PSUU

There are several ways to run and use the PSUU package. This guide shows you the different options.

## 1. Using the Python API

The most flexible way is to use PSUU as a Python library in your own scripts:

```python
from psuu import PsuuExperiment

# Create and configure experiment
experiment = PsuuExperiment(simulation_command="your_command")
experiment.add_kpi("metric", column="value", operation="max")
experiment.set_parameter_space({"param1": (0, 1), "param2": [1, 2, 3]})
experiment.set_optimizer(method="random", objective_name="metric")

# Run optimization
results = experiment.run()
```

## 2. Using the CLI as a Module

You can run PSUU using Python's module execution syntax:

```bash
# Activate your virtual environment first
source .venv/bin/activate

# Run PSUU as a module
python -m psuu init
python -m psuu add-param --name "param1" --range 0 1
python -m psuu add-kpi --name "metric" --column "value" --operation "max"
python -m psuu set-optimizer --method "random" --objective "metric"
python -m psuu run

# Or with uv run (if using uv package manager)
uv run python -m psuu init
uv run python -m psuu run
```

## 3. Using the Installed CLI Command

If the package is correctly installed with pip/uv, you can use the `psuu` command directly:

```bash
# Activate your virtual environment first
source .venv/bin/activate

# Run PSUU commands
psuu init
psuu add-param --name "param1" --range 0 1
psuu run
```

## 4. Using the Script in bin Directory

You can also run the script directly from the bin directory:

```bash
# Activate your virtual environment first
source .venv/bin/activate

# Run PSUU using the bin script
./bin/psuu init
./bin/psuu run
```

## 5. Using a Custom Script

You can create your own script that uses PSUU:

```bash
# Create a script
cat > run_psuu.py << 'EOF'
#!/usr/bin/env python
from psuu.cli import main

if __name__ == "__main__":
    main()
EOF

# Make it executable
chmod +x run_psuu.py

# Run it
./run_psuu.py init
./run_psuu.py run
```

## Troubleshooting

### Command Not Found

If you get a "command not found" error when trying to use `psuu` directly:

1. Make sure you've activated your virtual environment
2. Try reinstalling the package with:
   ```bash
   pip install -e .
   ```
3. Check if the entry point was installed:
   ```bash
   which psuu
   ```
   It should point to a location in your virtual environment.

### "No module named 'psuu'" Error

If you get "No module named 'psuu'" when trying to import or run the package:

1. Make sure you've installed the package with `pip install -e .`
2. Make sure you're in the right virtual environment
3. Check your PYTHONPATH:
   ```bash
   python -c "import sys; print(sys.path)"
   ```
   The project directory should be in the path.

### Other CLI Issues

If you have other issues with the CLI:

1. Try running directly with the module syntax:
   ```bash
   python -c "from psuu.cli import main; main()" init
   ```
2. Check if the CLI module has the correct shebang line and is executable
3. Verify that the `entry_points` section in `setup.py` is correct
