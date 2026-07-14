import json
from passprobe import PassProbe
from compilers import qiskit_compiler_fn, tket_compiler_fn, cirq_compiler_fn, bqskit_compiler_fn

# Common mock gate error model based on roughly standard NISQ values
MOCK_GATE_ERRORS = {
    'cx': 0.01,
    'cz': 0.01,
    'cnot': 0.01,
    'rz': 0.001,
    'sx': 0.001,
    'x': 0.001,
    'h': 0.002,
    'u3': 0.003,
    'rx': 0.001,
    'ry': 0.001,
    'z': 0.001,
    'tk1': 0.002,
    'tk2': 0.01,
    'rzgate': 0.001,
    'hgate': 0.002,
    'cnotgate': 0.01,
    'u3gate': 0.003
}

def run_qiskit_example():
    print("\n--- Qiskit PassProbe ---")
    from qiskit.circuit import QuantumCircuit
    from qiskit.transpiler.passes import (
        CommutativeCancellation, Optimize1qGatesDecomposition,
        RemoveBarriers, Depth
    )
    
    # Create simple circuit
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.rz(0.5, 2)
    qc.cx(1, 2)
    qc.barrier()
    qc.cx(0, 1)
    qc.cx(0, 1) # Redundant
    
    # List of passes to evaluate
    passes = [
        RemoveBarriers(),
        CommutativeCancellation(),
        Optimize1qGatesDecomposition(basis=['u3', 'cx']),
    ]
    
    probe = PassProbe(qiskit_compiler_fn, MOCK_GATE_ERRORS)
    results = probe.analyze(qc, passes)
    
    print("Shapley Values:", json.dumps(results['shapley_values'], indent=2))
    print("Concentration Ratios:", json.dumps(results['concentration_ratios'], indent=2))
    print("Ordering Sensitivity:", results['ordering_sensitivity'])


def run_tket_example():
    print("\n--- tket PassProbe ---")
    from pytket.circuit import Circuit
    from pytket.passes import CommuteThroughMultis, RemoveRedundancies, SimplifyInitial
    
    # Create simple circuit
    circ = Circuit(3)
    circ.H(0)
    circ.CX(0, 1)
    circ.CX(1, 2)
    circ.Rz(0.5, 2)
    circ.CX(1, 2)
    circ.CX(0, 1)
    circ.CX(0, 1)
    
    passes = [
        CommuteThroughMultis(),
        RemoveRedundancies(),
        SimplifyInitial()
    ]
    
    probe = PassProbe(tket_compiler_fn, MOCK_GATE_ERRORS)
    results = probe.analyze(circ, passes)
    
    print("Shapley Values:", json.dumps(results['shapley_values'], indent=2))
    print("Concentration Ratios:", json.dumps(results['concentration_ratios'], indent=2))
    print("Ordering Sensitivity:", results['ordering_sensitivity'])


def run_cirq_example():
    print("\n--- Cirq PassProbe ---")
    import cirq
    from cirq.transformers import drop_empty_moments, merge_single_qubit_gates_to_phxz, drop_negligible_operations
    
    q0, q1, q2 = cirq.LineQubit.range(3)
    circ = cirq.Circuit(
        cirq.H(q0),
        cirq.CNOT(q0, q1),
        cirq.CNOT(q1, q2),
        cirq.rz(0.5)(q2),
        cirq.CNOT(q1, q2),
        cirq.Moment(), # empty moment
        cirq.CNOT(q0, q1),
        cirq.CNOT(q0, q1)
    )
    
    passes = [
        drop_empty_moments,
        drop_negligible_operations,
        merge_single_qubit_gates_to_phxz
    ]
    
    probe = PassProbe(cirq_compiler_fn, MOCK_GATE_ERRORS)
    results = probe.analyze(circ, passes)
    
    print("Shapley Values:", json.dumps(results['shapley_values'], indent=2))
    print("Concentration Ratios:", json.dumps(results['concentration_ratios'], indent=2))
    print("Ordering Sensitivity:", results['ordering_sensitivity'])


def run_bqskit_example():
    print("\n--- BQSKit PassProbe ---")
    from bqskit.ir import Circuit
    from bqskit.ir.gates import CNOTGate, RZGate, HGate
    from bqskit.passes import UnfoldPass, ToU3Pass
    
    circ = Circuit(3)
    circ.append_gate(HGate(), [0])
    circ.append_gate(CNOTGate(), [0, 1])
    circ.append_gate(CNOTGate(), [1, 2])
    circ.append_gate(RZGate(0.5), [2])
    circ.append_gate(CNOTGate(), [1, 2])
    circ.append_gate(CNOTGate(), [0, 1])
    circ.append_gate(CNOTGate(), [0, 1])
    
    passes = [
        UnfoldPass(),
        ToU3Pass()
    ]
    
    probe = PassProbe(bqskit_compiler_fn, MOCK_GATE_ERRORS)
    results = probe.analyze(circ, passes)
    
    print("Shapley Values:", json.dumps(results['shapley_values'], indent=2))
    print("Concentration Ratios:", json.dumps(results['concentration_ratios'], indent=2))
    print("Ordering Sensitivity:", results['ordering_sensitivity'])


if __name__ == "__main__":
    run_qiskit_example()
    run_tket_example()
    run_cirq_example()
    run_bqskit_example()
