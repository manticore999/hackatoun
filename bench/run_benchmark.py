"""Benchmark: every policy on every crisis through the same simulator, same score.

Run:  python bench/run_benchmark.py --policies fifo nearest max_customers optimised --crises all
Output: bench/results/<timestamp>.csv + a chart (ours vs baselines, mean and spread).
"""
import argparse

from dispatch.config import load_config
from dispatch.data.loaders import list_crises


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policies", nargs="+", default=["fifo", "nearest", "max_customers", "optimised"])
    parser.add_argument("--crises", nargs="+", default=["all"])
    args = parser.parse_args()

    cfg = load_config()
    crises = list_crises(cfg) if args.crises == ["all"] else args.crises
    print(f"{len(crises)} crises x {len(args.policies)} policies")
    raise NotImplementedError("Benchmark workstream: needs Simulator.run() and the policies")


if __name__ == "__main__":
    main()
