"""Source generators for latent trajectory design.

Each generator signature:
    fn(n_steps, sr_latent, seed, **params) -> np.ndarray shape (n_steps,)

sr_latent = sample_rate / block_size  (~23.4 Hz for 48 kHz / 2048)
seed is an int used to initialise a local numpy Generator; deterministic
generators (sine, pulse, constant) ignore it.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Lorenz attractor
# ---------------------------------------------------------------------------


def _lorenz_euler(
    n_steps: int, sigma: float, rho: float, beta: float, dt: float, x0: float, y0: float, z0: float
):
    xs = np.empty(n_steps)
    ys = np.empty(n_steps)
    zs = np.empty(n_steps)
    x, y, z = x0, y0, z0
    for i in range(n_steps):
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        x += dx * dt
        y += dy * dt
        z += dz * dt
        xs[i] = x
        ys[i] = y
        zs[i] = z
    return xs, ys, zs


def lorenz(
    n_steps: int,
    sr_latent: float,
    seed: int,
    component: str = "x",
    sigma: float = 10.0,
    rho: float = 28.0,
    beta: float = 2.667,
    scale: float = 0.1,
    dt: float = 0.01,
    init=None,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if init is None:
        x0, y0, z0 = rng.uniform(-1.0, 1.0, 3)
    else:
        x0, y0, z0 = init

    xs, ys, zs = _lorenz_euler(n_steps, sigma, rho, beta, dt, x0, y0, z0)
    out = {"x": xs, "y": ys, "z": zs}[component]
    return (out * scale).astype(np.float64)


# ---------------------------------------------------------------------------
# Brownian motion
# ---------------------------------------------------------------------------


def brownian(
    n_steps: int, sr_latent: float, seed: int, sigma: float = 0.05, clip=None
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    steps = rng.normal(0.0, sigma, n_steps)
    trajectory = np.cumsum(steps)
    if clip is not None:
        trajectory = np.clip(trajectory, clip[0], clip[1])
    return trajectory


# ---------------------------------------------------------------------------
# Sine wave
# ---------------------------------------------------------------------------


def sine(
    n_steps: int,
    sr_latent: float,
    seed: int,
    freq_hz: float = 0.1,
    amplitude: float = 1.0,
    phase: float = 0.0,
) -> np.ndarray:
    t = np.arange(n_steps) / sr_latent
    return amplitude * np.sin(2.0 * np.pi * freq_hz * t + phase)


# ---------------------------------------------------------------------------
# Pulse (hard square wave)
# ---------------------------------------------------------------------------


def pulse(
    n_steps: int,
    sr_latent: float,
    seed: int,
    rate_hz: float = 0.1,
    duty: float = 0.5,
    amplitude: float = 2.0,
) -> np.ndarray:
    t = np.arange(n_steps) / sr_latent
    phase = (t * rate_hz) % 1.0
    return np.where(phase < duty, amplitude, 0.0)


# ---------------------------------------------------------------------------
# Constant
# ---------------------------------------------------------------------------


def constant(n_steps: int, sr_latent: float, seed: int, value: float = 0.0) -> np.ndarray:
    return np.full(n_steps, float(value))


# ---------------------------------------------------------------------------
# White noise / random
# ---------------------------------------------------------------------------


def random(
    n_steps: int, sr_latent: float, seed: int, distribution: str = "uniform", scale: float = 1.0
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if distribution == "uniform":
        return rng.uniform(-scale, scale, n_steps)
    elif distribution == "normal":
        return rng.normal(0.0, scale, n_steps)
    else:
        raise ValueError(f"Unknown distribution: {distribution!r}")


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

REGISTRY: dict = {
    "lorenz": lorenz,
    "brownian": brownian,
    "sine": sine,
    "pulse": pulse,
    "constant": constant,
    "random": random,
}


def make_source(algo_type: str, n_steps: int, sr_latent: float, seed: int, **params) -> np.ndarray:
    if algo_type not in REGISTRY:
        raise ValueError(f"Unknown algorithm type {algo_type!r}. Available: {list(REGISTRY)}")
    return REGISTRY[algo_type](n_steps, sr_latent, seed, **params)
