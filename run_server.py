"""Run PSUU server with template model.

API Documentation:
----------------

Model Connection:
POST /api/models/test-connection
    Test connection to simulation model
    Request: {
        "type": "protocol" | "cli",
        "details": {
            "moduleClass": str,  # For protocol connection
            "protocol": str,     # For protocol connection
            "command": str,      # For CLI connection
            "paramFormat": str,  # For CLI connection
            "outputFormat": str, # For CLI connection
            "workingDir": str    # For CLI connection
        }
    }
    Response: {
        "success": bool,
        "message": str
    }

Parameters:
GET /api/parameters
    Get model parameter space definition
    Response: [
        {
            "name": str,
            "type": "continuous" | "integer" | "categorical",
            "min": float,      # For continuous/integer
            "max": float,      # For continuous/integer
            "values": list,    # For categorical
            "description": str  # Optional
        }
    ]

POST /api/parameters
    Update parameter space configuration
    Request: {
        "parameters": [Parameter]
    }

KPIs:
GET /api/kpis
    Get available KPI definitions
    Response: [
        {
            "name": str,
            "type": "custom",
            "isObjective": bool,
            "maximize": bool
        }
    ]

POST /api/kpis
    Update KPI configuration
    Request: {
        "kpis": [KPI]
    }

Optimization:
POST /api/optimization/configure
    Configure optimization settings
    Request: {
        "method": "grid" | "random" | "bayesian",
        "iterations": int,
        "initialPoints": int,  # For bayesian
        "seed": int           # Optional
    }

POST /api/optimization/start
    Start optimization process
    Response: {
        "jobId": str,
        "status": str,
        "progress": int
    }

GET /api/optimization/stream
    Stream optimization updates (Server-Sent Events)
    Events:
        - step: Simulation step update
        - complete: Final results
        - error: Error message
"""

from psuu import PsuuExperiment
from template.model import SIRModel
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json
import time
import queue
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Initialize model
model = SIRModel()

# Initialize experiment with model
experiment = PsuuExperiment(
    simulation_command="python -m template.model",  # Command to run the model
    param_format="--{name} {value}",  # Format for passing parameters
    output_format="json"  # Expected output format
)
experiment.model = model  # Set the model instance

# Queue for streaming updates
updates_queue = queue.Queue()
optimization_running = False

def run_optimization():
    """Run optimization and send updates to queue."""
    global optimization_running
    optimization_running = True
    
    try:
        # Simulate optimization steps
        for i in range(10):
            # Run simulation
            params = {
                'beta': 0.3 + i * 0.02,
                'gamma': 0.1,
                'population': 1000
            }
            result = model.run(params)
            
            # Send update
            update = {
                'type': 'step',
                'step': i + 1,
                'command': f"Running simulation with params: {json.dumps(params)}",
                'result': {
                    'parameters': params,
                    'kpis': result.kpis
                }
            }
            updates_queue.put(update)
            time.sleep(1)  # Simulate computation time
        
        # Send final results
        updates_queue.put({
            'type': 'complete',
            'result': {
                'bestParameters': {
                    'beta': 0.3,
                    'gamma': 0.1,
                    'population': 1000
                },
                'bestKPIs': {
                    'peak_infected': 300,
                    'total_infected': 800,
                    'epidemic_duration': 45,
                    'r0': 3.0
                },
                'iterations': 10,
                'elapsedTime': 10.5
            }
        })
    except Exception as e:
        updates_queue.put({
            'type': 'error',
            'message': str(e)
        })
    finally:
        optimization_running = False

@app.route('/api/models/test-connection', methods=['POST'])
def test_connection():
    """Test connection to simulation model."""
    data = request.json
    if data['type'] == 'protocol' and data['details']['moduleClass'] == 'template.model.SIRModel':
        return jsonify({'success': True, 'message': 'Connected to template SIR model'})
    return jsonify({'success': False, 'message': 'Invalid model configuration'})

@app.route('/api/parameters', methods=['GET', 'POST'])
def parameters():
    """Get or update parameter space configuration."""
    if request.method == 'GET':
        param_space = model.get_parameter_space()
        parameters = []
        for name, config in param_space.items():
            if isinstance(config, tuple):
                parameters.append({
                    'name': name,
                    'type': 'continuous',
                    'min': config[0],
                    'max': config[1]
                })
            elif isinstance(config, list):
                parameters.append({
                    'name': name,
                    'type': 'categorical',
                    'values': config
                })
        return jsonify(parameters)
    else:  # POST
        try:
            data = request.json
            parameters = data.get('parameters', [])
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/kpis', methods=['GET', 'POST'])
def kpis():
    """Get or update KPI configuration."""
    if request.method == 'GET':
        kpi_defs = model.get_kpi_definitions()
        kpis = []
        for name in kpi_defs:
            kpis.append({
                'name': name,
                'type': 'custom',
                'isObjective': False,
                'maximize': True
            })
        return jsonify(kpis)
    else:  # POST
        try:
            data = request.json
            kpis = data.get('kpis', [])
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/optimization/configure', methods=['POST'])
def configure_optimization():
    """Configure optimization settings."""
    try:
        config = request.json
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/optimization/start', methods=['POST'])
def start_optimization():
    """Start optimization process."""
    global optimization_running
    if not optimization_running:
        # Start optimization in a new thread
        threading.Thread(target=run_optimization, daemon=True).start()
        return jsonify({
            'jobId': 'test-job-1',
            'status': 'running',
            'progress': 0
        })
    return jsonify({'error': 'Optimization already running'}), 400

@app.route('/api/optimization/stream')
def stream_optimization():
    """Stream optimization updates."""
    def generate():
        while True:
            try:
                update = updates_queue.get(timeout=1.0)
                yield f"data: {json.dumps(update)}\n\n"
                if update['type'] in ['complete', 'error']:
                    break
            except queue.Empty:
                if not optimization_running:
                    break
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print("\nPSUU Template Model Server")
    print("=========================")
    print("Connect using:")
    print("1. Protocol Integration")
    print("2. Model Class: template.model.SIRModel")
    print("3. Protocol: cadcad")
    print("\nServer running at http://localhost:5000")
    app.run(port=5000, debug=True, threaded=True)
