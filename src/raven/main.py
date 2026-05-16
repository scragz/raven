#!/usr/bin/env python3
"""Raven — RAVE Latent Trajectory Generator.

Usage:
    raven [config.py] [--debug]
    python -m raven [config.py] [--debug]
"""

import argparse
import importlib
import importlib.util
import logging
import sys
from pathlib import Path

import numpy as np

from .generator import run_batch
from .model import RAVEModel
from .sweep import sweep_dimensions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if path.exists():
        spec = importlib.util.spec_from_file_location("_raven_config", path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load config from {config_path!r}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    elif config_path == "config.py":
        logger.info("No ./config.py found; using bundled raven.config defaults")
        mod = importlib.import_module(".config", package=__package__)
    else:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    return {
        "model": mod.model,
        "global_config": mod.global_config,
        "sweep": mod.sweep,
        "sources": mod.sources,
        "collections": mod.collections,
        "batch": mod.batch,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Raven: RAVE Latent Trajectory Generator")
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
        seed = int(np.random.default_rng().integers(0, 2**31))
    np.random.seed(seed)
    logger.info(f"Global seed: {seed}")

    # Load and verify model
    model = RAVEModel(config["model"])

    # Sweep (or load cache)
    sweep_cache = sweep_dimensions(model, config["model"], config["sweep"])
    n_active = len(sweep_cache["active_dims"])
    logger.info(f"Active dims: {n_active}  →  {sweep_cache['active_dims']}")

    if n_active == 0:
        logger.error("No active dims found. Lower sweep.threshold or check your model.")
        return 1

    # Check that every collection's routing can be satisfied
    max_requested_slots = 0
    for name in config["batch"]:
        coll = config["collections"][name]
        max_requested_slots = max(max_requested_slots, len(coll["routing"]))
        n_routed = sum(
            1
            for key in coll["routing"]
            if key.startswith("active_") and int(key.split("_", 1)[1]) < n_active
        )
        if n_routed == 0:
            logger.error(
                f"Collection {name!r}: no routing entries match the {n_active} active dim(s)."
            )
            return 1
    if n_active < max_requested_slots:
        logger.warning(
            f"Presets define up to {max_requested_slots} routing slots; "
            f"this model exposes {n_active} active dim(s), so extra slots will be ignored."
        )

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
        print(f"\n{total_warnings} out-of-range warning(s) logged. Check sidecar JSON for details.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
