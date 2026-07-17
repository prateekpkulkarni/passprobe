# ⚙️🔍 PassProbe: Quantifying Compiler Pass Contributions in Quantum Transpilation

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-success.svg)](LICENSE)

PassProbe is a mathematically rigorous framework designed to evaluate the true marginal contribution of individual transpiler passes in quantum compilation pipelines. Based on the paper _"PassProbe: Quantifying Compiler Pass Contributions in Quantum Transpilation"_ ([paper draft](passprobe_draft.pdf)), this tool utilizes cooperative game theory (specifically Shapley Values) to attribute circuit quality improvements fairly across interconnected compiler passes.

<p align="center">
  <img src="PassProbe_Frame.svg" alt="PassProbe Framework" width="900">
</p>

## Features
- **Cross-Compiler Support**: Built-in adapter functions to natively support **Qiskit**, **pytket**, **Cirq**, and **BQSKit**.
- **Combinatorial Evaluation**: Exhaustively evaluates $2^k$ pass subsets to track non-linear pass interactions.
- **Expected Fidelity Tracking**: Uses customizable gate-error models to accurately quantify a circuit's resistance to NISQ-era decoherence and gate errors.
- **Derived Metrics**: Automatically computes Normalized Attribution ($\hat{\phi}_i$), Concentration Ratios ($\text{CR}_m$), and Ordering Sensitivity ($\Omega$).

## Installation

Ensure you have Python 3.8+ installed. You can install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

This will install the core numerical libraries alongside the four supported quantum transpilation frameworks.

## Project Structure

- `passprobe.py`: The core algorithm for Shapley evaluation and metric computation. 
- `compilers.py`: Contains the `compiler_fn` adapters that connect PassProbe to Qiskit, tket, Cirq, and BQSKit.
- `example_usage.py`: A comprehensive script demonstrating how to construct circuits, define pass lists, and run PassProbe for all four compiler frameworks.

## Quick Start

You can verify the setup and see PassProbe in action by running the provided demonstration script:

```bash
python example_usage.py
```

### Example: Using PassProbe with Qiskit

To integrate PassProbe into your own project with Qiskit, simply import the framework, provide a gate error dictionary, and supply a list of Qiskit transpiler passes:

```python
from qiskit.circuit import QuantumCircuit
from qiskit.transpiler.passes import RemoveBarriers, CommutativeCancellation
from passprobe import PassProbe
from compilers import qiskit_compiler_fn

# Define a mock error model (or derive from backend properties)
gate_errors = {'cx': 0.01, 'rz': 0.001, 'u3': 0.003}

# Create your circuit
qc = QuantumCircuit(2)
qc.cx(0, 1)

# List the passes you want to evaluate
passes_to_evaluate = [RemoveBarriers(), CommutativeCancellation()]

# Initialize the probe
probe = PassProbe(compiler_fn=qiskit_compiler_fn, gate_error_model=gate_errors)

# Run the analysis
results = probe.analyze(qc, passes_to_evaluate)

print(results['shapley_values'])
print(results['ordering_sensitivity'])
```
## Reproducing Paper Figures

We provide a generalized, CLI-driven plotting engine (`plotting.py`) to reproduce the main figures from the PassProbe paper (Figures 2, 3, 4, and 5) directly from the ablation experiment logs. 

### Dependencies
Ensure you have the required data processing and plotting libraries installed:
```bash
pip install pandas matplotlib seaborn numpy
```
# Generating the Plots

Once you have run the PassProbe ablation engine and generated the result CSVs, you can produce all publication-ready figures using the plotting script.

To generate all figures at once, provide the paths to each results file and specify an output directory:

```bash
python plotting.py \
    --shapley results/shapley_aggregated.csv \
    --concentration results/concentration_metrics.csv \
    --structural results/structural_drivers.csv \
    --ordering results/ordering_sensitivity.csv \
    --pruning results/pruning_effects.csv \
    --out_dir figures/
```

The script will generate the following publication-ready PDF figures in the specified output directory:

- `figure_2_shapley_heatmap.pdf` — Shapley attribution by pass category.
- `figure_3_concentration.pdf` — Concentration ratios and negligible-pass analysis.
- `figure_4_structural_drivers.pdf` — Correlations between logical connectivity, idle-time potential, and compiler pass contributions.
- `figure_5_ordering_pruning.pdf` — Pass ordering sensitivity and compiler pipeline pruning results.

## Generating Individual Figures

Each figure can also be generated independently. For example, if only the structural-driver analysis has been updated, regenerate Figure&nbsp;4 by providing only the corresponding input file:

```bash
python plotting.py \
    --structural results/new_structural_drivers.csv \
    --out_dir figures/
```

Similarly, any other figure can be regenerated by supplying only its corresponding command-line argument.


## How It Works

1. **Pass Subsets**: PassProbe generates all combinations (subsets) of the provided passes.
2. **Evaluation**: For each subset, it compiles the circuit and calculates the resulting **Expected Fidelity** by checking the types and quantities of gates remaining, mapping them to the provided `gate_error_model`.
3. **Attribution**: It calculates the exact Shapley value for each pass, indicating how much that specific pass contributed to the final fidelity, averaged over every possible context (presence or absence of other passes).

## License
MIT License
