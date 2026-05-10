"""Dimension sweep: rank RAVE latent dims by how much they affect audio output.

Cache format (written alongside the model file as <model_name>.sweep.json):
    {
        "active_dims":    [7, 3, 11, 2, ...],   # indices ranked by rms_variance, above threshold
        "observed_ranges": {"7": [-1.2, 1.4], ...},  # latent input range where dim produces audible output
        "rms_variance":   {"7": 0.43, ...}       # variance of per-step RMS across the sweep
    }

observed_ranges[dim] = [min_input, max_input] over the sweep steps where the
decoded audio RMS is above a small noise floor (1e-4).  This is the "active
input region" for that dimension.  At decode time a warning is emitted when a
source drives a dim outside its observed range.
"""

import json
import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

_NOISE_FLOOR = 1e-4


def _cache_path(model_path: str) -> Path:
    return Path(model_path).with_suffix(".sweep.json")


def _load_cache(model_path: str) -> dict:
    path = _cache_path(model_path)
    with open(path) as f:
        data = json.load(f)
    data["active_dims"] = [int(d) for d in data["active_dims"]]
    return data


def _run_sweep(model, model_cfg: dict, sweep_cfg: dict) -> dict:
    n_latents = model_cfg["n_latents"]
    lo, hi = sweep_cfg["range"]
    steps = sweep_cfg["steps"]
    var_threshold = sweep_cfg["threshold"]

    values = np.linspace(lo, hi, steps)
    rms_variances: dict[int, float] = {}
    observed_ranges: dict[int, list] = {}

    logger.info(f"Sweeping {n_latents} latent dims ({steps} steps each)…")

    for dim in range(n_latents):
        rms_vals = np.empty(steps)
        for i, v in enumerate(values):
            latent = np.zeros(n_latents)
            latent[dim] = float(v)
            audio = model.decode(latent)
            rms_vals[i] = float(np.sqrt(np.mean(audio ** 2)))

        variance = float(np.var(rms_vals))
        rms_variances[dim] = variance

        # Active input range: sweep values that produced audible output
        active_inputs = values[rms_vals > _NOISE_FLOOR]
        if len(active_inputs) >= 2:
            observed_ranges[dim] = [float(active_inputs[0]), float(active_inputs[-1])]
        else:
            # Dim appears silent; fall back to full sweep range
            observed_ranges[dim] = [float(lo), float(hi)]

        logger.debug(
            f"  dim {dim:2d}: var={variance:.5f}  "
            f"range={observed_ranges[dim]}"
        )

    # Rank by variance descending, filter by threshold
    ranked = sorted(rms_variances.items(), key=lambda kv: -kv[1])
    active_dims = [dim for dim, var in ranked if var > var_threshold]

    logger.info(
        f"Active dims ({len(active_dims)} of {n_latents}): {active_dims}"
    )

    return {
        "active_dims": active_dims,
        "observed_ranges": {str(k): v for k, v in observed_ranges.items()},
        "rms_variance": {str(k): float(v) for k, v in rms_variances.items()},
    }


def sweep_dimensions(model, model_cfg: dict, sweep_cfg: dict) -> dict:
    """Return sweep results, running the sweep or loading from cache as needed."""
    cache_path = _cache_path(model_cfg["path"])
    enabled = sweep_cfg["enabled"]
    use_cache = sweep_cfg["cache"]

    if not enabled:
        if cache_path.exists():
            logger.info(f"Sweep disabled; loading cache from {cache_path}")
            return _load_cache(model_cfg["path"])
        raise RuntimeError(
            f"sweep.enabled is False but no cache found at {cache_path}. "
            "Run with sweep.enabled=True at least once to generate the cache."
        )

    if use_cache and cache_path.exists():
        logger.info(f"Loading sweep cache from {cache_path}")
        return _load_cache(model_cfg["path"])

    result = _run_sweep(model, model_cfg, sweep_cfg)

    if use_cache:
        with open(cache_path, "w") as f:
            json.dump(result, f, indent=2)
        logger.info(f"Sweep cache written to {cache_path}")

    return result
