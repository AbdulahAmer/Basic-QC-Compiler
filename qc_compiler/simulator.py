"""Minimal state-vector quantum circuit simulator built on numpy.

Qubits are 1-indexed. Qubit 1 is the least significant bit of the state
index and is printed as the leftmost character of a measured bitstring.
"""

from collections import Counter

import numpy as np

I = np.identity(2)
X = np.array([[0, 1], [1, 0]])
Y = np.array([[0, -1j], [1j, 0]])
Z = np.array([[1, 0], [0, -1]])
H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)

# |0><0| and |1><1| projectors, used to build controlled gates
P0 = np.array([[1, 0], [0, 0]])
P1 = np.array([[0, 0], [0, 1]])

GATES = {"I": I, "X": X, "Y": Y, "Z": Z, "H": H}
CONTROLLED_GATES = {"CX": X, "CY": Y, "CZ": Z}


def get_ground_state(num_qubits):
    """Return the |0...0> state: a vector of size 2**num_qubits with a 1 in the first slot."""
    state = np.zeros(2**num_qubits, dtype=complex)
    state[0] = 1
    return state


def _kron_on(total_qubits, placements):
    """Tensor product of 2x2 matrices, with `placements` {qubit: matrix} and identity elsewhere."""
    O = np.array([[1]])
    for qubit in range(total_qubits, 0, -1):
        O = np.kron(O, placements.get(qubit, I))
    return O


def get_operator(total_qubits, gate, target_qubits):
    """Return the 2**n x 2**n operator for `gate` acting on `target_qubits`.

    Single-qubit gates take one target. Controlled gates take [control, target] and are
    built as P0(control) + P1(control) (x) U(target).
    """
    gate = gate.upper()
    for q in target_qubits:
        if not 1 <= q <= total_qubits:
            raise ValueError(f"qubit {q} out of range for a {total_qubits}-qubit circuit")

    if gate in CONTROLLED_GATES:
        control, target = target_qubits
        if control == target:
            raise ValueError("control and target qubits must differ")
        U = CONTROLLED_GATES[gate]
        return _kron_on(total_qubits, {control: P0}) + _kron_on(total_qubits, {control: P1, target: U})

    if gate in GATES:
        (target,) = target_qubits
        return _kron_on(total_qubits, {target: GATES[gate]})

    raise ValueError(f"unknown gate {gate!r}; supported: {sorted(GATES) + sorted(CONTROLLED_GATES)}")


def run_program(initial_state, program):
    """Apply each {"gate": ..., "target": [...]} step in `program` and return the final state."""
    psi = np.asarray(initial_state, dtype=complex)
    total_qubits = int(np.log2(len(psi)))
    for step in program:
        psi = get_operator(total_qubits, step["gate"], step["target"]) @ psi
    return psi


def _bitstring(index, total_qubits):
    return format(index, f"0{total_qubits}b")[::-1]


def measure_all(state_vector, rng=None):
    """Sample one basis state using |amplitude|**2 as weights and return it as a bitstring."""
    rng = rng or np.random.default_rng()
    probabilities = np.abs(state_vector) ** 2
    total_qubits = int(np.log2(len(state_vector)))
    index = rng.choice(len(state_vector), p=probabilities / probabilities.sum())
    return _bitstring(index, total_qubits)


def get_counts(state_vector, num_shots, rng=None):
    """Measure `num_shots` times and return {bitstring: occurrences} for outcomes that occurred."""
    rng = rng or np.random.default_rng()
    return dict(Counter(measure_all(state_vector, rng) for _ in range(num_shots)))
