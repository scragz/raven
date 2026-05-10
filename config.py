model = {
    "path": "./models/guitar.ts",
    "attrs": {},
    "sample_rate": 48000,
    "block_size": 2048,
    "n_latents": 16,
}

global_config = {
    "output_dir": "./output/",
    "duration": 30.0,
    "seed": 12345,
    "normalize": False,
}

sweep = {
    "enabled": True,
    "cache": True,
    "range": [-3.0, 3.0],
    "steps": 100,
    "threshold": 0.05,
}

algorithms = {
    "lorenz_slow": {
        "type": "lorenz",
        "component": "x",
        "sigma": 10.0, "rho": 28.0, "beta": 2.667,
        "scale": 0.05,
        "dt": 0.01,
    },
    "lorenz_wide": {
        "type": "lorenz",
        "component": "x",
        "sigma": 10.0, "rho": 28.0, "beta": 2.667,
        "scale": 0.3,
        "dt": 0.01,
    },
    "lorenz_x": {
        "type": "lorenz",
        "component": "x",
        "sigma": 10.0, "rho": 28.0, "beta": 2.667,
        "scale": 0.1,
        "dt": 0.01,
    },
    "lorenz_y": {
        "type": "lorenz",
        "component": "y",
        "sigma": 10.0, "rho": 28.0, "beta": 2.667,
        "scale": 0.1,
        "dt": 0.01,
    },
    "lorenz_z": {
        "type": "lorenz",
        "component": "z",
        "sigma": 10.0, "rho": 28.0, "beta": 2.667,
        "scale": 0.1,
        "dt": 0.01,
    },
    "brown_narrow": {
        "type": "brownian",
        "sigma": 0.05,
        "clip": [-1.0, 1.0],
    },
    "brown_wide": {
        "type": "brownian",
        "sigma": 0.3,
        "clip": [-3.0, 3.0],
    },
    "brown_slow": {
        "type": "brownian",
        "sigma": 0.01,
        "clip": [-2.0, 2.0],
    },
    "sine_slow": {
        "type": "sine",
        "freq_hz": 0.05,
        "amplitude": 1.0,
        "phase": 0.0,
    },
    "sine_med": {
        "type": "sine",
        "freq_hz": 0.3,
        "amplitude": 1.5,
        "phase": 0.0,
    },
    "pulse_slow": {
        "type": "pulse",
        "rate_hz": 0.1,
        "duty": 0.5,
        "amplitude": 2.0,
    },
    "pulse_fast": {
        "type": "pulse",
        "rate_hz": 1.0,
        "duty": 0.2,
        "amplitude": 2.0,
    },
    "constant_high": {
        "type": "constant",
        "value": 2.5,
    },
    "constant_mid": {
        "type": "constant",
        "value": 1.0,
    },
    "constant_zero": {
        "type": "constant",
        "value": 0.0,
    },
}

collections = {
    "coherent_chaos": {
        "description": "all active dims from same attractor, correlated drift",
        "unassigned": "zero",
        "routing": {
            "active_0": ("lorenz_slow", 1.0),
            "active_1": ("lorenz_slow", 1.0),
            "active_2": ("lorenz_slow", 1.0),
            "active_3": ("lorenz_slow", 1.0),
        },
    },
    "multi_attractor": {
        "description": "different lorenz components per dim, correlated but not identical",
        "unassigned": "zero",
        "routing": {
            "active_0": ("lorenz_x", 1.0),
            "active_1": ("lorenz_y", 1.0),
            "active_2": ("lorenz_z", 1.0),
            "active_3": ("lorenz_x", -1.0),
        },
    },
    "tension": {
        "description": "pinned dims vs wide-swinging dims",
        "unassigned": "zero",
        "routing": {
            "active_0": ("constant_mid", 1.0),
            "active_1": ("constant_mid", 1.0),
            "active_2": ("lorenz_wide", 1.0),
            "active_3": ("lorenz_wide", -1.0),
        },
    },
    "drift": {
        "description": "pure brownian at different rates, no periodicity",
        "unassigned": "noise",
        "routing": {
            "active_0": ("brown_slow", 1.0),
            "active_1": ("brown_narrow", 1.0),
            "active_2": ("brown_wide", 1.0),
            "active_3": ("brown_slow", -1.0),
        },
    },
    "pulse": {
        "description": "rhythmic switching, hard transitions through latent space",
        "unassigned": "zero",
        "routing": {
            "active_0": ("pulse_slow", 1.0),
            "active_1": ("pulse_fast", 1.0),
            "active_2": ("pulse_slow", -1.0),
            "active_3": ("constant_zero", 1.0),
        },
    },
    "frozen": {
        "description": "one dim moving, rest pinned — isolates single decoder axis",
        "unassigned": "zero",
        "routing": {
            "active_0": ("lorenz_slow", 1.0),
            "active_1": ("constant_zero", 1.0),
            "active_2": ("constant_zero", 1.0),
            "active_3": ("constant_zero", 1.0),
        },
    },
    "opposition": {
        "description": "dims moving against each other from same source",
        "unassigned": "zero",
        "routing": {
            "active_0": ("lorenz_wide", 1.0),
            "active_1": ("lorenz_wide", -1.0),
            "active_2": ("brown_wide", 1.0),
            "active_3": ("brown_wide", -1.0),
        },
    },
    "outside": {
        "description": "push dims beyond trained range, decoder hallucinates out-of-distribution coordinates",
        "unassigned": "zero",
        "routing": {
            "active_0": ("constant_high", 1.0),
            "active_1": ("constant_high", 1.0),
            "active_2": ("lorenz_wide", 1.0),
            "active_3": ("constant_zero", 1.0),
        },
    },
}

batch = [
    "coherent_chaos",
    "multi_attractor",
    "tension",
    "drift",
    "pulse",
    "frozen",
    "opposition",
    "outside",
]
