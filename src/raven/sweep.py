"""Dimension sweep: rank RAVE latent dims by how much they affect audio output.

Cache format (written alongside the model file as <model_name>.sweep.json):
    {
        "active_dims":      [7, 3, 11, 2, ...],  # indices ranked by combined score, above threshold
        "observed_ranges":  {"7": [-1.2, 1.4], ...},
        "rms_variance":     {"7": 0.43, ...},
        "timbral_variance": {"7": 1820.4, ...}   # variance of spectral centroid across sweep
    }

Ranking uses a combined score:
    score = normalised(rms_variance) + timbral_weight * normalised(timbral_variance)

so that dims which modulate timbre without strongly changing energy are not
buried at the bottom of the active_dims list.  timbral_weight defaults to 0.2
and can be set in sweep config.
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


def _cache_matches(data: dict, model_cfg: dict, sweep_cfg: dict) -> bool:
    params = data.get("sweep")
    expected = {
        "n_latents": model_cfg["n_latents"],
        "range": sweep_cfg["range"],
        "steps": sweep_cfg["steps"],
        "threshold": sweep_cfg["threshold"],
        "timbral_weight": sweep_cfg.get("timbral_weight", 0.2),
    }
    return params == expected


def _spectral_centroid(audio: np.ndarray, sr: int) -> float:
    fft_mag = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(len(audio), d=1.0 / sr)
    total = float(np.sum(fft_mag))
    if total < 1e-10:
        return 0.0
    return float(np.dot(freqs, fft_mag) / total)


def _run_sweep(model, model_cfg: dict, sweep_cfg: dict) -> dict:
    n_latents = model_cfg["n_latents"]
    sr = model_cfg["sample_rate"]
    lo, hi = sweep_cfg["range"]
    steps = sweep_cfg["steps"]
    var_threshold = sweep_cfg["threshold"]
    timbral_weight = sweep_cfg.get("timbral_weight", 0.2)

    values = np.linspace(lo, hi, steps)
    rms_variances: dict[int, float] = {}
    timbral_variances: dict[int, float] = {}
    observed_ranges: dict[int, list] = {}

    logger.info(f"Sweeping {n_latents} latent dims ({steps} steps each)…")

    for dim in range(n_latents):
        rms_vals = np.empty(steps)
        centroid_vals = np.empty(steps)

        for i, v in enumerate(values):
            latent = np.zeros(n_latents)
            latent[dim] = float(v)
            audio = model.decode(latent)
            rms_vals[i] = float(np.sqrt(np.mean(audio**2)))
            centroid_vals[i] = _spectral_centroid(audio, sr)

        rms_variances[dim] = float(np.var(rms_vals))
        timbral_variances[dim] = float(np.var(centroid_vals))

        active_inputs = values[rms_vals > _NOISE_FLOOR]
        if len(active_inputs) >= 2:
            observed_ranges[dim] = [float(active_inputs[0]), float(active_inputs[-1])]
        else:
            observed_ranges[dim] = [float(lo), float(hi)]

        logger.debug(
            f"  dim {dim:2d}: rms_var={rms_variances[dim]:.5f}  "
            f"tmb_var={timbral_variances[dim]:.1f}  range={observed_ranges[dim]}"
        )

    # Combined ranking: normalise both metrics to [0,1] then blend
    rms_arr = np.array([rms_variances[d] for d in range(n_latents)])
    tmb_arr = np.array([timbral_variances[d] for d in range(n_latents)])
    rms_norm = rms_arr / (rms_arr.max() + 1e-12)
    tmb_norm = tmb_arr / (tmb_arr.max() + 1e-12)
    combined = {d: float(rms_norm[d] + timbral_weight * tmb_norm[d]) for d in range(n_latents)}

    ranked = sorted(combined.items(), key=lambda kv: -kv[1])
    # Filter: must exceed rms threshold to qualify as active at all
    active_dims = [dim for dim, _ in ranked if rms_variances[dim] > var_threshold]

    logger.info(f"Active dims ({len(active_dims)} of {n_latents}): {active_dims}")

    return {
        "sweep": {
            "n_latents": n_latents,
            "range": sweep_cfg["range"],
            "steps": steps,
            "threshold": var_threshold,
            "timbral_weight": timbral_weight,
        },
        "active_dims": active_dims,
        "observed_ranges": {str(k): v for k, v in observed_ranges.items()},
        "rms_variance": {str(k): float(v) for k, v in rms_variances.items()},
        "timbral_variance": {str(k): float(v) for k, v in timbral_variances.items()},
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
        cached = _load_cache(model_cfg["path"])
        if _cache_matches(cached, model_cfg, sweep_cfg):
            logger.info(f"Loading sweep cache from {cache_path}")
            return cached
        logger.info(f"Sweep cache at {cache_path} does not match current parameters; rebuilding")

    result = _run_sweep(model, model_cfg, sweep_cfg)

    if use_cache:
        with open(cache_path, "w") as f:
            json.dump(result, f, indent=2)
        logger.info(f"Sweep cache written to {cache_path}")

    return result
