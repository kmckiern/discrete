import pprint
from collections import OrderedDict

import dimod
import dwavebinarycsp as dbc

# https://github.com/dwavesystems/factoring-demo/blob/master/factoring/interfaces.py
P = 12
n_bits = 3
min_classical_gap = 0.1
n_reads = 50

### FORMULATE PROBLEM
csp = dbc.factories.multiplication_circuit(n_bits)
bqm = dbc.stitch(csp, min_classical_gap=min_classical_gap)

p_vars = ['p{}'.format(i) for i in n_bits*2]
fixed_variables = dict(zip(reversed(p_vars), "{:06b}".format(P)))
fixed_variables = {var: int(x) for (var, x) in fixed_variables.items()}
for var, value in fixed_variables.items():
    bqm.fix_variable(var, value)

### RUN
sampler = dimod.SimulatedAnnealingSampler()
response = sampler.sample(bqm, num_reads=n_reads)

### RESULTS
a_vars = ['a{}'.format(i) for i in n_bits]
b_vars = ['b{}'.format(i) for i in n_bits]
if 'num_occurrences' not in response.data_vectors:
    response.data_vectors['num_occurrences'] = [1] * len(response)
total = sum(response.data_vectors['num_occurrences'])
assert total == n_reads

results_dict = OrderedDict()
for sample, num_occurrences in response.data(['sample', 'num_occurrences']):
    a = b = 0
    for lbl in reversed(a_vars):
        a = (a << 1) | sample[lbl]
    for lbl in reversed(b_vars):
        b = (b << 1) | sample[lbl]
    a, b = int(a), int(b)

    if (a, b, P) in results_dict:
        results_dict[(a, b, P)]["numOfOccurrences"] += num_occurrences
    else:
        results_dict[(a, b, P)] = {"a": a,
                                   "b": b,
                                   "valid": a * b == P,
                                   "numOfOccurrences": num_occurrences}

output = {
    "results": list(results_dict.values()),
    "numberOfReads": total
}
pprint.PrettyPrinter(depth=4).pprint(output)
