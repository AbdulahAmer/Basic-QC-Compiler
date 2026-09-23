"""Command-line entry point: run a circuit and print measurement counts."""

import argparse
import json
import sys

import numpy as np

from .simulator import get_counts, get_ground_state, run_program


def parse_gate(spec):
    """Parse 'H:1' or 'CX:1,2' into a program step."""
    try:
        gate, targets = spec.split(":")
        return {"gate": gate, "target": [int(t) for t in targets.split(",")]}
    except ValueError:
        raise argparse.ArgumentTypeError(f"bad gate {spec!r}, expected GATE:q or GATE:c,t (e.g. H:1, CX:1,2)")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="qc-compiler",
        description="Simulate a quantum circuit and print measurement counts.",
        epilog="Example: qc-compiler -g H:1 -g CX:1,2 --shots 1000",
    )
    parser.add_argument("circuit", nargs="?", help="JSON file with a list of {gate, target} steps ('-' for stdin)")
    parser.add_argument("-g", "--gate", action="append", type=parse_gate, default=[],
                        help="gate step as GATE:q or GATE:c,t; repeatable, appended after the circuit file")
    parser.add_argument("-n", "--qubits", type=int, help="number of qubits (default: highest qubit used)")
    parser.add_argument("-s", "--shots", type=int, default=1000, help="number of measurements (default: 1000)")
    parser.add_argument("--seed", type=int, help="random seed for reproducible counts")
    parser.add_argument("--state", action="store_true", help="also print the final state vector")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    program = []
    if args.circuit:
        f = sys.stdin if args.circuit == "-" else open(args.circuit)
        with f:
            program = json.load(f)
    program += args.gate
    if not program:
        parser.error("no circuit given; pass a JSON file or --gate steps")

    num_qubits = args.qubits or max(q for step in program for q in step["target"])

    try:
        state = run_program(get_ground_state(num_qubits), program)
    except ValueError as e:
        parser.error(str(e))

    if args.state:
        print("state:", np.round(state, 6))
    counts = get_counts(state, args.shots, np.random.default_rng(args.seed))
    for bits, count in sorted(counts.items()):
        print(f"{bits}  {count}")
    return 0
