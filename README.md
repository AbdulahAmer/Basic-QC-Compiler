# Basic QC Compiler

A minimal quantum circuit simulator written with numpy. It started as Task 3 for the
Quantum Open Software Foundation mentorship program. The original notebook is kept as
`QOSF spring attempt-deprecated-2021-02-14.ipynb`.

## Install

```sh
pip install -e .
```

## Usage

Pass a circuit as a JSON file, as `--gate` steps, or both:

```sh
qc-compiler examples/bell.json --shots 1000
qc-compiler -g H:1 -g CX:1,2 --shots 1000 --state
echo '[{"gate": "H", "target": [1]}]' | python -m qc_compiler -
```

```
00  507
11  493
```

- Gates: `I X Y Z H` (one target) and `CX CY CZ` (`control,target`)
- Qubits are 1-indexed. Qubit 1 is the leftmost character of each output bitstring
- `-n/--qubits` sets the circuit size. By default it is the highest qubit used
- `--seed` makes the counts reproducible

## As a library

```python
from qc_compiler import get_ground_state, run_program, get_counts

state = run_program(get_ground_state(2), [{"gate": "H", "target": [1]}, {"gate": "CX", "target": [1, 2]}])
get_counts(state, 1000)
```
