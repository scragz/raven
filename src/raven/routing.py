"""Routing resolution and latent matrix construction.

Routing keys in config use the symbolic form "active_N" which maps to the
Nth entry of sweep_cache["active_dims"] (ranked by RMS variance).

build_latents returns a (n_steps, n_latents) float64 array and a list of
warning strings for any source values that exceed the observed input range
for their routed dimension.
"""

import hashlib
import logging

import numpy as np

from .sources import make_source

logger = logging.getLogger(__name__)


def _derive_seed(global_seed: int, algo_name: str, dim: int) -> int:
    """Stable, order-independent per-source seed derived from global seed."""
    key = f"{global_seed}:{algo_name}:{dim}"
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**31)


def resolve_routing(collection_routing: dict, active_dims: list) -> dict:
    """Map active_N symbolic keys to actual latent dimension indices.

    Returns:
        {dim_index: (algo_name, gain), ...}
    """
    resolved: dict[int, tuple] = {}
    for key, (algo_name, gain) in collection_routing.items():
        if not key.startswith("active_"):
            raise ValueError(f"Invalid routing key {key!r}. Expected format: active_<int>")
        idx = int(key.split("_", 1)[1])
        if idx >= len(active_dims):
            continue
        resolved[active_dims[idx]] = (algo_name, gain)
    return resolved


def _fit_to_observed_range(values: np.ndarray, lo: float, hi: float, margin: float) -> np.ndarray:
    """Scale one source trajectory into a dimension's observed latent range."""
    center = (lo + hi) * 0.5
    half_width = (hi - lo) * 0.5 * margin
    if half_width <= 0.0:
        return np.full_like(values, center)

    vmin = float(values.min())
    vmax = float(values.max())
    if np.isclose(vmin, vmax):
        if vmax > 0.0:
            return np.full_like(values, center + half_width)
        if vmax < 0.0:
            return np.full_like(values, center - half_width)
        return np.full_like(values, min(max(0.0, center - half_width), center + half_width))

    normalized = ((values - vmin) / (vmax - vmin)) * 2.0 - 1.0
    return center + normalized * half_width


def build_latents(
    n_steps: int,
    n_latents: int,
    resolved_routing: dict,
    unassigned_policy: str,
    algorithms_cfg: dict,
    global_seed: int,
    sr_latent: float,
    sweep_cache: dict,
    fit_observed: bool = False,
    fit_margin: float = 0.95,
) -> tuple:
    """Build the (n_steps, n_latents) latent matrix.

    Returns:
        (latents, warnings)  where warnings is a list of str
    """
    latents = np.zeros((n_steps, n_latents), dtype=np.float64)
    warnings: list[str] = []

    # --- unassigned dims ---
    for dim in range(n_latents):
        if dim in resolved_routing:
            continue
        if unassigned_policy == "zero":
            pass  # already zero
        elif unassigned_policy == "noise":
            seed = _derive_seed(global_seed, f"__noise_policy_{dim}", dim)
            rng = np.random.default_rng(seed)
            latents[:, dim] = rng.normal(0.0, 0.01, n_steps)
        elif unassigned_policy.startswith("constant:"):
            val = float(unassigned_policy.split(":", 1)[1])
            latents[:, dim] = val
        else:
            raise ValueError(f"Unknown unassigned policy: {unassigned_policy!r}")

    # --- routed dims ---
    observed_ranges = sweep_cache.get("observed_ranges", {})

    for dim, (algo_name, gain) in resolved_routing.items():
        algo_cfg = algorithms_cfg[algo_name]
        algo_type = algo_cfg["type"]
        params = {k: v for k, v in algo_cfg.items() if k != "type"}
        seed = _derive_seed(global_seed, algo_name, dim)

        source = make_source(algo_type, n_steps, sr_latent, seed, **params)
        values = source * gain

        # Out-of-observed-range warning
        obs = observed_ranges.get(str(dim))
        if obs is not None:
            lo, hi = obs
            exceeds_observed = bool(np.any((values < lo) | (values > hi)))
            should_fit = fit_observed is True or fit_observed == "always"
            should_fit = should_fit or (fit_observed == "if_needed" and exceeds_observed)
            if should_fit:
                values = _fit_to_observed_range(values, lo, hi, fit_margin)
            out_mask = (values < lo) | (values > hi)
            n_out = int(out_mask.sum())
            if n_out:
                warnings.append(
                    f"dim {dim} ({algo_name} × {gain:+.2f}): "
                    f"{n_out}/{n_steps} steps outside observed range "
                    f"[{lo:.3f}, {hi:.3f}]"
                )

        latents[:, dim] = values

    return latents, warnings
