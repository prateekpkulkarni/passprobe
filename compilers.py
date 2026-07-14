from collections import Counter

# --- Qiskit ---
def qiskit_compiler_fn(circuit, passes):
    from qiskit.transpiler import PassManager
    
    # We create a pass manager with the selected subset of passes
    pm = PassManager(passes)
    compiled_circ = pm.run(circuit)
    
    # Count gates
    gate_counts = Counter()
    for instruction in compiled_circ.data:
        gate_counts[instruction.operation.name.lower()] += 1
    return dict(gate_counts)

# --- tket ---
def tket_compiler_fn(circuit, passes):
    from pytket.passes import SequencePass
    # In pytket, circuit is modified in place, so we make a copy
    circ_copy = circuit.copy()
    
    # Run the selected passes in sequence
    if passes:
        seq_pass = SequencePass(passes)
        seq_pass.apply(circ_copy)
    
    # Count gates
    gate_counts = Counter()
    for cmd in circ_copy.get_commands():
        gate_counts[cmd.op.type.name.lower()] += 1
    return dict(gate_counts)

# --- Cirq ---
def cirq_compiler_fn(circuit, passes):
    import cirq
    
    # Make a copy of the circuit
    compiled_circ = circuit.unfreeze() if isinstance(circuit, cirq.FrozenCircuit) else circuit.copy()
    
    # Apply passes sequentially
    for p in passes:
        if hasattr(p, 'optimize_circuit'):
            p.optimize_circuit(compiled_circ)
        elif callable(p):
            p(compiled_circ)
            
    # Count gates
    gate_counts = Counter()
    for moment in compiled_circ:
        for op in moment:
            if op.gate:
                gate_name = str(op.gate).split('(')[0].split('**')[0].lower()
                gate_counts[gate_name] += 1
    return dict(gate_counts)

# --- BQSKit ---
def bqskit_compiler_fn(circuit, passes):
    from bqskit.compiler import Compiler
    
    if not passes:
        gate_counts = Counter()
        for op in circuit:
            gate_counts[op.gate.name.lower()] += 1
        return dict(gate_counts)
        
    # Using BQSKit compiler to execute a workflow of passes
    with Compiler() as compiler:
        compiled_circ = compiler.compile(circuit, passes)
        
    # Count gates
    gate_counts = Counter()
    for op in compiled_circ:
        gate_counts[op.gate.name.lower()] += 1
    return dict(gate_counts)
