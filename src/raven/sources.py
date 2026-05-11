"""Source generators for latent trajectory design.

Each generator signature:
    fn(n_steps, sr_latent, seed, **params) -> np.ndarray shape (n_steps,)

sr_latent = sample_rate / block_size  (~23.4 Hz for 48 kHz / 2048)
seed is an int used to initialise a local numpy Generator; deterministic
generators (sine, pulse, constant) ignore it.
"""

import numpy as np


def _centered_peak_scale(values: np.ndarray, scale: float) -> np.ndarray:
    centered = values - np.mean(values)
    peak = float(np.max(np.abs(centered)))
    if peak <= 1e-12:
        return np.zeros_like(values, dtype=np.float64)
    return (centered / peak * scale).astype(np.float64)


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
# Rossler attractor
# ---------------------------------------------------------------------------


def rossler(
    n_steps: int,
    sr_latent: float,
    seed: int,
    component: str = "x",
    a: float = 0.2,
    b: float = 0.2,
    c: float = 5.7,
    dt: float = 0.04,
    scale: float = 0.2,
    init=None,
) -> np.ndarray:
    """Rossler attractor with RK4 integration."""
    rng = np.random.default_rng(seed)
    if init is None:
        x, y, z = rng.uniform(-1.0, 1.0, 3)
    else:
        x, y, z = init

    xs = np.empty(n_steps)
    ys = np.empty(n_steps)
    zs = np.empty(n_steps)

    def deriv(state_x: float, state_y: float, state_z: float) -> tuple[float, float, float]:
        return -state_y - state_z, state_x + a * state_y, b + state_z * (state_x - c)

    for i in range(n_steps):
        k1x, k1y, k1z = deriv(x, y, z)
        k2x, k2y, k2z = deriv(
            x + 0.5 * dt * k1x,
            y + 0.5 * dt * k1y,
            z + 0.5 * dt * k1z,
        )
        k3x, k3y, k3z = deriv(
            x + 0.5 * dt * k2x,
            y + 0.5 * dt * k2y,
            z + 0.5 * dt * k2z,
        )
        k4x, k4y, k4z = deriv(x + dt * k3x, y + dt * k3y, z + dt * k3z)
        x += (dt / 6.0) * (k1x + 2.0 * k2x + 2.0 * k3x + k4x)
        y += (dt / 6.0) * (k1y + 2.0 * k2y + 2.0 * k3y + k4y)
        z += (dt / 6.0) * (k1z + 2.0 * k2z + 2.0 * k3z + k4z)
        xs[i] = x
        ys[i] = y
        zs[i] = z

    out = {"x": xs, "y": ys, "z": zs}[component]
    return _centered_peak_scale(out, scale)


# ---------------------------------------------------------------------------
# Duffing oscillator
# ---------------------------------------------------------------------------


def duffing(
    n_steps: int,
    sr_latent: float,
    seed: int,
    component: str = "x",
    delta: float = 0.2,
    alpha: float = -1.0,
    beta: float = 1.0,
    gamma: float = 0.37,
    omega: float = 1.2,
    dt: float = 0.05,
    scale: float = 1.0,
    init=None,
) -> np.ndarray:
    """Forced Duffing oscillator with RK4 integration."""
    rng = np.random.default_rng(seed)
    if init is None:
        x, v = rng.uniform(-0.5, 0.5, 2)
    else:
        x, v = init

    xs = np.empty(n_steps)
    vs = np.empty(n_steps)

    def deriv(state_x: float, state_v: float, time: float) -> tuple[float, float]:
        accel = gamma * np.cos(omega * time) - delta * state_v - alpha * state_x - beta * state_x**3
        return state_v, accel

    time = 0.0
    for i in range(n_steps):
        k1x, k1v = deriv(x, v, time)
        k2x, k2v = deriv(x + 0.5 * dt * k1x, v + 0.5 * dt * k1v, time + 0.5 * dt)
        k3x, k3v = deriv(x + 0.5 * dt * k2x, v + 0.5 * dt * k2v, time + 0.5 * dt)
        k4x, k4v = deriv(x + dt * k3x, v + dt * k3v, time + dt)
        x += (dt / 6.0) * (k1x + 2.0 * k2x + 2.0 * k3x + k4x)
        v += (dt / 6.0) * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)
        time += dt
        xs[i] = x
        vs[i] = v

    out = {"x": xs, "v": vs}[component]
    return (out * scale).astype(np.float64)


# ---------------------------------------------------------------------------
# Discrete strange attractor maps
# ---------------------------------------------------------------------------


def henon(
    n_steps: int,
    sr_latent: float,
    seed: int,
    component: str = "x",
    a: float = 1.4,
    b: float = 0.3,
    scale: float = 1.0,
    init=None,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if init is None:
        x, y = rng.uniform(-0.2, 0.2, 2)
    else:
        x, y = init

    xs = np.empty(n_steps)
    ys = np.empty(n_steps)
    for i in range(n_steps):
        x, y = 1.0 - a * x * x + y, b * x
        xs[i] = x
        ys[i] = y

    out = {"x": xs, "y": ys}[component]
    return (out * scale).astype(np.float64)


def ikeda(
    n_steps: int,
    sr_latent: float,
    seed: int,
    component: str = "x",
    u: float = 0.918,
    scale: float = 0.7,
    init=None,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if init is None:
        x, y = rng.uniform(-0.5, 0.5, 2)
    else:
        x, y = init

    xs = np.empty(n_steps)
    ys = np.empty(n_steps)
    for i in range(n_steps):
        t = 0.4 - 6.0 / (1.0 + x * x + y * y)
        sin_t = np.sin(t)
        cos_t = np.cos(t)
        x, y = 1.0 + u * (x * cos_t - y * sin_t), u * (x * sin_t + y * cos_t)
        xs[i] = x
        ys[i] = y

    out = {"x": xs, "y": ys}[component]
    return (out * scale).astype(np.float64)


def standard_map(
    n_steps: int,
    sr_latent: float,
    seed: int,
    component: str = "sin",
    k: float = 5.2,
    drift: float = 0.0,
    scale: float = 1.0,
    init=None,
) -> np.ndarray:
    """Chaotic Chirikov standard map on a wrapped phase plane."""
    rng = np.random.default_rng(seed)
    if init is None:
        theta = rng.uniform(0.0, 2.0 * np.pi)
        momentum = rng.uniform(-np.pi, np.pi)
    else:
        theta, momentum = init

    values = np.empty(n_steps)
    for i in range(n_steps):
        momentum = (momentum + k * np.sin(theta) + drift + np.pi) % (2.0 * np.pi) - np.pi
        theta = (theta + momentum) % (2.0 * np.pi)
        if component == "sin":
            value = np.sin(theta)
        elif component == "cos":
            value = np.cos(theta)
        elif component == "momentum":
            value = momentum / np.pi
        else:
            raise ValueError(f"Unknown standard_map component: {component!r}")
        values[i] = value

    return (values * scale).astype(np.float64)


# ---------------------------------------------------------------------------
# Coupled map lattice
# ---------------------------------------------------------------------------


def logistic_lattice(
    n_steps: int,
    sr_latent: float,
    seed: int,
    n_cells: int = 128,
    r: float = 3.92,
    coupling: float = 0.18,
    substeps: int = 8,
    statistic: str = "energy",
    cell: int = 0,
    scale: float = 5.0,
) -> np.ndarray:
    """Coupled logistic-map lattice; intentionally expensive for tangled motion."""
    rng = np.random.default_rng(seed)
    state = rng.uniform(0.05, 0.95, n_cells)
    out = np.empty(n_steps)

    for i in range(n_steps):
        for _ in range(substeps):
            mapped = r * state * (1.0 - state)
            state = (1.0 - coupling) * mapped + 0.5 * coupling * (
                np.roll(mapped, 1) + np.roll(mapped, -1)
            )
            state = np.clip(state, 0.0, 1.0)

        if statistic == "cell":
            value = state[cell % n_cells]
        elif statistic == "mean":
            value = float(np.mean(state))
        elif statistic == "gradient":
            value = float(np.mean(np.abs(state - np.roll(state, 1))))
        elif statistic == "energy":
            centered = state - np.mean(state)
            value = float(np.mean(centered * centered))
        else:
            raise ValueError(f"Unknown logistic_lattice statistic: {statistic!r}")
        out[i] = value

    return _centered_peak_scale(out, scale)


# ---------------------------------------------------------------------------
# 1D Gray-Scott reaction diffusion
# ---------------------------------------------------------------------------


def reaction_diffusion(
    n_steps: int,
    sr_latent: float,
    seed: int,
    n_cells: int = 192,
    substeps: int = 16,
    feed: float = 0.037,
    kill: float = 0.06,
    du: float = 0.16,
    dv: float = 0.08,
    statistic: str = "spot",
    cell: int = 0,
    scale: float = 8.0,
) -> np.ndarray:
    """One-dimensional Gray-Scott system projected to a latent trajectory."""
    rng = np.random.default_rng(seed)
    u = np.ones(n_cells)
    v = np.zeros(n_cells)
    center = n_cells // 2
    width = max(4, n_cells // 12)
    sl = slice(center - width, center + width)
    u[sl] = rng.uniform(0.35, 0.65, width * 2)
    v[sl] = rng.uniform(0.2, 0.35, width * 2)
    u += rng.normal(0.0, 0.015, n_cells)
    v += rng.normal(0.0, 0.015, n_cells)

    out = np.empty(n_steps)
    for i in range(n_steps):
        for _ in range(substeps):
            lap_u = np.roll(u, 1) + np.roll(u, -1) - 2.0 * u
            lap_v = np.roll(v, 1) + np.roll(v, -1) - 2.0 * v
            uvv = u * v * v
            u += du * lap_u - uvv + feed * (1.0 - u)
            v += dv * lap_v + uvv - (feed + kill) * v
            u = np.clip(u, 0.0, 1.2)
            v = np.clip(v, 0.0, 1.2)

        if statistic == "spot":
            value = v[cell % n_cells]
        elif statistic == "mass":
            value = float(np.mean(v))
        elif statistic == "edge":
            value = float(np.mean(np.abs(v - np.roll(v, 1))))
        elif statistic == "centroid":
            total = float(np.sum(v))
            value = 0.0 if total <= 1e-12 else float(np.dot(np.arange(n_cells), v) / total)
        else:
            raise ValueError(f"Unknown reaction_diffusion statistic: {statistic!r}")
        out[i] = value

    return _centered_peak_scale(out, scale)


# ---------------------------------------------------------------------------
# Binary cellular automata
# ---------------------------------------------------------------------------


def cellular_automaton(
    n_steps: int,
    sr_latent: float,
    seed: int,
    rule: int = 30,
    n_cells: int = 257,
    substeps: int = 4,
    statistic: str = "edge",
    cell: int = 0,
    scale: float = 2.0,
) -> np.ndarray:
    """Elementary cellular automaton projected through density/edge probes."""
    rng = np.random.default_rng(seed)
    state = rng.integers(0, 2, n_cells, dtype=np.uint8)
    table = np.array([(rule >> idx) & 1 for idx in range(8)], dtype=np.uint8)
    weights = np.hanning(n_cells)
    out = np.empty(n_steps)

    for i in range(n_steps):
        for _ in range(substeps):
            left = np.roll(state, 1)
            right = np.roll(state, -1)
            idx = (left << 2) | (state << 1) | right
            state = table[idx]

        if statistic == "density":
            value = float(np.mean(state))
        elif statistic == "edge":
            value = float(np.mean(state != np.roll(state, 1)))
        elif statistic == "cell":
            value = float(state[cell % n_cells])
        elif statistic == "window":
            value = float(np.dot(state, weights) / np.sum(weights))
        else:
            raise ValueError(f"Unknown cellular_automaton statistic: {statistic!r}")
        out[i] = value

    return _centered_peak_scale(out, scale)


# ---------------------------------------------------------------------------
# Random additive/FM oscillator bank
# ---------------------------------------------------------------------------


def oscillator_bank(
    n_steps: int,
    sr_latent: float,
    seed: int,
    n_oscillators: int = 96,
    min_freq_hz: float = 0.01,
    max_freq_hz: float = 4.0,
    fm_depth: float = 0.8,
    feedback: float = 0.15,
    scale: float = 1.0,
) -> np.ndarray:
    """Dense beating oscillator cloud with slow random FM and phase feedback."""
    rng = np.random.default_rng(seed)
    freqs = np.exp(rng.uniform(np.log(min_freq_hz), np.log(max_freq_hz), n_oscillators))
    phases = rng.uniform(0.0, 2.0 * np.pi, n_oscillators)
    amps = rng.normal(0.0, 1.0, n_oscillators) / np.sqrt(n_oscillators)
    fm_freqs = rng.uniform(0.003, 0.12, n_oscillators)
    fm_phases = rng.uniform(0.0, 2.0 * np.pi, n_oscillators)

    out = np.empty(n_steps)
    last = 0.0
    for i in range(n_steps):
        t = i / sr_latent
        fm = 1.0 + fm_depth * np.sin(2.0 * np.pi * fm_freqs * t + fm_phases)
        phases += (2.0 * np.pi * freqs * fm / sr_latent) + feedback * last
        voices = np.sin(phases) + 0.35 * np.sin(phases * 2.01 + last)
        last = float(np.tanh(np.dot(amps, voices)))
        out[i] = last

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
    "rossler": rossler,
    "duffing": duffing,
    "henon": henon,
    "ikeda": ikeda,
    "standard_map": standard_map,
    "logistic_lattice": logistic_lattice,
    "reaction_diffusion": reaction_diffusion,
    "cellular_automaton": cellular_automaton,
    "oscillator_bank": oscillator_bank,
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
