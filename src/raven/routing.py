"""Routing resolution and latent matrix construction.

Routing keys use "active_N" which maps to the Nth entry of
sweep_cache["active_dims"] (ranked by combined RMS + timbral score).

Each routing value is a list of contribution dicts:

    [{"src": str, "gain": float, "offset": float, "smooth": float}, ...]

    src    – name of a source defined in the config sources dict
    gain   – multiply source trajectory (default 1.0)
    offset – add after gain (default 0.0)
    smooth – IIR lowpass coefficient in [0, 1); 0 = no smoothing (default 0.0)
             y[n] = smooth * y[n-1] + (1-smooth) * x[n]

When multiple contributions in a collection share the same "src" name they
reference the *same* generated trajectory — this is how correlated control
across dimensions is achieved.  The per-source seed is derived only from the
global seed and the source name, not the dimension index.
"""

import hashlib
import logging

import numpy as np

from .sources import make_source

logger = logging.getLogger(__name__)


def _derive_seed(global_seed: int, src_name: str) -> int:
    """Stable seed derived from global seed and source name only.

    Deliberately excludes dimension index so that two dims routing the same
    source name get the same trajectory, enabling correlation.
    """
    key = f"{global_seed}:{src_name}"
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**31)


def _normalize_contribution(c: dict) -> dict:
    if not isinstance(c, dict):
        raise TypeError(
            f"Each routing contribution must be a dict with at least a 'src' key, got {type(c)}"
        )
    if "src" not in c:
        raise ValueError(f"Contribution dict missing required 'src' key: {c!r}")
    return {
        "src": c["src"],
        "gain": float(c.get("gain", 1.0)),
        "offset": float(c.get("offset", 0.0)),
        "smooth": float(c.get("smooth", 0.0)),
    }


def _apply_smooth(values: np.ndarray, coeff: float) -> np.ndarray:
    """First-order IIR lowpass.  coeff=0 → pass-through; close to 1 → very slow."""
    out = np.empty_like(values)
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = coeff * out[i - 1] + (1.0 - coeff) * values[i]
    return out


def resolve_routing(collection_routing: dict, active_dims: list) -> dict:
    """Map active_N symbolic keys to actual latent dimension indices.

    Returns:
        {dim_index: [contribution_dict, ...], ...}
    """
    resolved: dict[int, list] = {}
    for key, contributions in collection_routing.items():
        if not key.startswith("active_"):
            raise ValueError(f"Invalid routing key {key!r}. Expected format: active_<int>")
        idx = int(key.split("_", 1)[1])
        if idx >= len(active_dims):
            continue
        dim = active_dims[idx]
        resolved[dim] = [_normalize_contribution(c) for c in contributions]
    return resolved


def _fit_to_observed_range(values: np.ndarray, lo: float, hi: float, margin: float) -> np.ndarray:
    """Linearly rescale a trajectory to fit within a dimension's observed range."""
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
    sources_cfg: dict,
    global_seed: int,
    sr_latent: float,
    sweep_cache: dict,
    fit_observed: bool | str = False,
    fit_margin: float = 0.95,
) -> tuple:
    """Build the (n_steps, n_latents) latent matrix.

    Sources referenced by name are generated once and shared across all dims
    that route them, producing correlated trajectories.

    Returns:
        (latents, warnings)  where warnings is a list of str
    """
    latents = np.zeros((n_steps, n_latents), dtype=np.float64)
    warnings: list[str] = []

    # --- Generate each unique source once ---
    all_src_names: set[str] = {
        c["src"] for contribs in resolved_routing.values() for c in contribs
    }
    source_cache: dict[str, np.ndarray] = {}
    for src_name in all_src_names:
        if src_name not in sources_cfg:
            raise ValueError(
                f"Source {src_name!r} not found in sources config. "
                f"Available: {sorted(sources_cfg)}"
            )
        cfg = sources_cfg[src_name]
        src_type = cfg["type"]
        params = {k: v for k, v in cfg.items() if k != "type"}
        seed = _derive_seed(global_seed, src_name)
        source_cache[src_name] = make_source(src_type, n_steps, sr_latent, seed, **params)

    # --- Unassigned dims ---
    for dim in range(n_latents):
        if dim in resolved_routing:
            continue
        if unassigned_policy == "zero":
            pass  # already zero
        elif unassigned_policy == "noise":
            seed = _derive_seed(global_seed, f"__noise_{dim}")
            rng = np.random.default_rng(seed)
            latents[:, dim] = rng.normal(0.0, 0.01, n_steps)
        elif unassigned_policy.startswith("constant:"):
            val = float(unassigned_policy.split(":", 1)[1])
            latents[:, dim] = val
        else:
            raise ValueError(f"Unknown unassigned policy: {unassigned_policy!r}")

    # --- Routed dims ---
    observed_ranges = sweep_cache.get("observed_ranges", {})

    for dim, contributions in resolved_routing.items():
        signal = np.zeros(n_steps)

        for contrib in contributions:
            raw = source_cache[contrib["src"]]
            values = raw * contrib["gain"] + contrib["offset"]
            if contrib["smooth"] > 0.0:
                values = _apply_smooth(values, contrib["smooth"])
            signal += values

        # Out-of-observed-range warning and optional rescaling
        obs = observed_ranges.get(str(dim))
        if obs is not None:
            lo, hi = obs
            exceeds = bool(np.any((signal < lo) | (signal > hi)))
            should_fit = fit_observed == "always" or (fit_observed == "if_needed" and exceeds)
            if should_fit:
                signal = _fit_to_observed_range(signal, lo, hi, fit_margin)
            out_mask = (signal < lo) | (signal > hi)
            n_out = int(out_mask.sum())
            if n_out:
                src_names = ", ".join(c["src"] for c in contributions)
                warnings.append(
                    f"dim {dim} ({src_names}): "
                    f"{n_out}/{n_steps} steps outside observed range [{lo:.3f}, {hi:.3f}]"
                )

        latents[:, dim] = signal

    return latents, warnings
