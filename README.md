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
Bell state |Φ+>
|00>  507
|11>  493
```

With `--state`, the final state is also printed in Dirac notation, e.g.
`state: 0.707|00> + 0.707|11>`.

- Gates: `I X Y Z H` (one target) and `CX CY CZ` (`control,target`)
- Qubits are 1-indexed. Qubit 1 is the leftmost character of each output bitstring
- `-n/--qubits` sets the circuit size. By default it is the highest qubit used
- `--seed` makes the counts reproducible
- A circuit file is either a plain list of steps or `{"name", "description", "circuit": [...]}`

## Examples

Classic circuits from the textbook canon, in [`examples/`](examples/). Run any of them with
`qc-compiler examples/<file> --state`.

| Circuit | Qubits | Expected measurement |
| --- | --- | --- |
| [Bell state \|Φ+>](examples/bell.json) | 2 | `\|00>` or `\|11>`, 50/50 |
| [Bell state \|Ψ->](examples/bell-psi-minus.json) | 2 | `\|01>` or `\|10>`, 50/50 (the state is `0.707\|01> - 0.707\|10>`) |
| [GHZ state](examples/ghz.json) | 3 | `\|000>` or `\|111>`, 50/50 |
| [Uniform superposition](examples/uniform-superposition.json) | 3 | all 8 states, about 1/8 each |
| [Single-qubit interference](examples/interference.json) | 1 | always `\|1>` (H Z H = X) |
| [SWAP from three CNOTs](examples/swap.json) | 2 | `\|10>` becomes `\|01>` |
| [Superdense coding](examples/superdense-coding.json) | 2 | always `\|11>`, the two bits Alice encoded |
| [Quantum teleportation](examples/teleportation.json) | 3 | qubit 3 is always 1: `\|xy1>` |
| [Deutsch-Jozsa](examples/deutsch-jozsa.json) | 3 | always `\|111>`: the oracle is balanced |
| [Bernstein-Vazirani](examples/bernstein-vazirani.json) | 4 | always `\|1011>`: the hidden string is `101` |
| [Grover search](examples/grover.json) | 2 | always `\|11>`, the marked item |

Each file's `description` field explains how the circuit works.

## As a library

```python
from qc_compiler import bra, format_state, get_counts, get_ground_state, ket, run_program

state = run_program(get_ground_state(2), [{"gate": "H", "target": [1]}, {"gate": "CX", "target": [1, 2]}])
get_counts(state, 1000)  # {'00': 507, '11': 493}
format_state(state)      # '0.707|00> + 0.707|11>'
ket("10"), bra("10")     # ('|10>', '<10|')
```
