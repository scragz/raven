#!/usr/bin/env python3
"""Raven — RAVE Latent Trajectory Generator.

Usage:
    python main.py [config.py] [--debug]
"""

import argparse
import importlib.util
import logging
import sys

import numpy as np

from generator import run_batch
from model import RAVEModel
from sweep import sweep_dimensions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    spec = importlib.util.spec_from_file_location("_raven_config", config_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {
        "model": mod.model,
        "global_config": mod.global_config,
        "sweep": mod.sweep,
        "algorithms": mod.algorithms,
        "collections": mod.collections,
        "batch": mod.batch,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Raven: RAVE Latent Trajectory Generator"
    )
    parser.add_argument(
        "config",
        nargs="?",
        default="config.py",
        help="Path to config.py (default: ./config.py)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    config = load_config(args.config)

    # Seed
    seed = config["global_config"].get("seed")
    if seed is None:
        seed = int(np.random.SeedSequence().entropy & 0x7FFF_FFFF)
    np.random.seed(seed)
    logger.info(f"Global seed: {seed}")

    # Load and verify model
    model = RAVEModel(config["model"])

    # Sweep (or load cache)
    sweep_cache = sweep_dimensions(model, config["model"], config["sweep"])
    n_active = len(sweep_cache["active_dims"])
    logger.info(f"Active dims: {n_active}  →  {sweep_cache['active_dims']}")

    if n_active == 0:
        logger.error(
            "No active dims found. Lower sweep.threshold or check your model."
        )
        return 1

    # Check that every collection's routing can be satisfied
    for name in config["batch"]:
        coll = config["collections"][name]
        for key in coll["routing"]:
            idx = int(key.split("_", 1)[1])
            if idx >= n_active:
                logger.error(
                    f"Collection {name!r}: routing key {key!r} requires "
                    f"at least {idx + 1} active dims, but only {n_active} found."
                )
                return 1

    # Generate
    results = run_batch(model, config, sweep_cache, seed)

    # Summary
    print(f"\nGenerated {len(results)} file(s):")
    for r in results:
        line = f"  {r['collection']:20s}  {r['wav']}"
        if r["warnings"]:
            line += f"  [{len(r['warnings'])} warning(s)]"
        print(line)

    total_warnings = sum(len(r["warnings"]) for r in results)
    if total_warnings:
        print(
            f"\n{total_warnings} out-of-range warning(s) logged. "
            "Check sidecar JSON for details."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
