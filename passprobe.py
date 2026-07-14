import itertools
import math
from collections import Counter
import random

class PassProbe:
    def __init__(self, compiler_fn, gate_error_model, max_ordering_samples=100):
        """
        Args:
            compiler_fn: A callable `fn(circuit, passes_subset)` that returns 
                         a list of gate names (or gate objects) that exist in the compiled circuit.
            gate_error_model: A dict mapping gate name to error rate (e.g., {'cx': 0.01, 'rz': 0.001}).
            max_ordering_samples: Max permutations to sample for ordering sensitivity.
        """
        self.compiler_fn = compiler_fn
        self.gate_error_model = gate_error_model
        self.max_ordering_samples = max_ordering_samples

    def evaluate_quality(self, circuit, passes_subset, permutation=None):
        if permutation is not None:
            # Reorder passes based on permutation
            ordered_passes = [passes_subset[i] for i in permutation]
        else:
            ordered_passes = passes_subset
            
        gate_counts = self.compiler_fn(circuit, ordered_passes)
        
        # Expected fidelity: Product of (1 - error_rate) for each gate
        fidelity = 1.0
        for gate, count in gate_counts.items():
            error_rate = self.gate_error_model.get(gate, 0.0) # default to 0 error if not specified
            fidelity *= math.pow((1 - error_rate), count)
        return fidelity

    def compute_shapley_values(self, circuit, passes):
        k = len(passes)
        passes_indices = list(range(k))
        
        # Precompute quality for all subsets
        # We evaluate subsets based on their indices to keep it generic
        quality_map = {}
        for r in range(k + 1):
            for subset in itertools.combinations(passes_indices, r):
                subset_passes = [passes[i] for i in subset]
                quality_map[subset] = self.evaluate_quality(circuit, subset_passes)
                
        shapley_values = {i: 0.0 for i in passes_indices}
        
        for r in range(k):
            for subset in itertools.combinations(passes_indices, r):
                for i in passes_indices:
                    if i not in subset:
                        S_union_i = tuple(sorted(list(subset) + [i]))
                        marginal_contrib = quality_map[S_union_i] - quality_map[subset]
                        weight = (math.factorial(len(subset)) * math.factorial(k - len(subset) - 1)) / math.factorial(k)
                        shapley_values[i] += weight * marginal_contrib
                        
        # Return mapped to actual passes, use index to distinguish identical passes if any
        # Assuming passes are objects, we use their string representation or class name
        def get_pass_name(p):
            if hasattr(p, 'name') and isinstance(p.name, str) and p.name: return p.name
            if hasattr(p, '__name__') and p.__name__: return p.__name__
            str_rep = str(p)
            if str_rep.startswith("<tket::") or "Pass" in str_rep:
                # e.g. <tket::CommuteThroughMultis ...>
                clean = str_rep.split()[0].strip("<>")
                if clean: return clean.split("::")[-1]
            return p.__class__.__name__

        return {get_pass_name(passes[i]): shapley_values[i] for i in passes_indices}, quality_map

    def compute_derived_metrics(self, shapley_values):
        total_abs_attribution = sum(abs(v) for v in shapley_values.values())
        if total_abs_attribution == 0:
             return {k: 0.0 for k in shapley_values}, {}
             
        normalized = {k: abs(v) / total_abs_attribution for k, v in shapley_values.items()}
        
        # Sort passes by normalized attribution descending
        sorted_passes = sorted(normalized.items(), key=lambda x: x[1], reverse=True)
        
        concentration_ratios = {}
        cumulative = 0.0
        for m, (pass_name, attr) in enumerate(sorted_passes, 1):
            cumulative += attr
            concentration_ratios[f"CR_{m}"] = cumulative
            
        return normalized, concentration_ratios

    def compute_ordering_sensitivity(self, circuit, passes_subset):
        k = len(passes_subset)
        if k == 0 or k == 1:
            return 0.0
            
        num_permutations = math.factorial(k)
        if num_permutations <= self.max_ordering_samples:
            permutations = list(itertools.permutations(range(k)))
        else:
            permutations = [tuple(random.sample(range(k), k)) for _ in range(self.max_ordering_samples)]
            
        max_q = -1.0
        min_q = float('inf')
        
        for perm in permutations:
            q = self.evaluate_quality(circuit, passes_subset, permutation=perm)
            max_q = max(max_q, q)
            min_q = min(min_q, q)
            
        q_default = self.evaluate_quality(circuit, passes_subset)
        if q_default == 0.0:
             return 0.0 # Avoid division by zero
        
        return (max_q - min_q) / q_default

    def analyze(self, circuit, passes):
        shapley, q_map = self.compute_shapley_values(circuit, passes)
        normalized, cr = self.compute_derived_metrics(shapley)
        
        # Ordering sensitivity on the full set of passes
        omega = self.compute_ordering_sensitivity(circuit, passes)
        
        return {
            'shapley_values': shapley,
            'normalized_attribution': normalized,
            'concentration_ratios': cr,
            'ordering_sensitivity': omega,
            'subset_qualities': q_map
        }
