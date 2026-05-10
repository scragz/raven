model_sax_soprano_franziskaschroeder_b2048_r48000_z20 = {
    "path": "./models/sax_soprano_franziskaschroeder_b2048_r48000_z20.ts",
    "n_latents": 20,
}

model_voice_vocalset_b2048_r48000_z16 = {
    "path": "./models/voice_vocalset_b2048_r48000_z16.ts",
    "n_latents": 16,
}

model_organ_archive_b2048_r48000_z16 = {
    "path": "./models/organ_archive_b2048_r48000_z16.ts",
    "n_latents": 16,
}


model_guitar_iil_b2048_r48000_z16 = {
    "path": "./models/guitar_iil_b2048_r48000_z16.ts",
    "n_latents": 16,
}

model = model_organ_archive_b2048_r48000_z16 | {
    "attrs": {},
    "sample_rate": 48000,
    "block_size": 2048,
}

global_config = {
    "output_dir": "./output/",
    "duration": 120.0,
    "seed": 98653861,
    "normalize": True,
}

sweep = {
    "enabled": True,
    "cache": True,
    "range": [-3.0, 3.0],
    "steps": 100,
    "threshold": 1e-6,
}

algorithms = {
    "lorenz_slow": {
        "type": "lorenz",
        "component": "x",
        "sigma": 10.0,
        "rho": 28.0,
        "beta": 2.667,
        "scale": 0.05,
        "dt": 0.01,
    },
    "lorenz_wide": {
        "type": "lorenz",
        "component": "x",
        "sigma": 10.0,
        "rho": 28.0,
        "beta": 2.667,
        "scale": 0.3,
        "dt": 0.01,
    },
    "lorenz_hot_x": {
        "type": "lorenz",
        "component": "x",
        "sigma": 10.0,
        "rho": 28.0,
        "beta": 2.667,
        "scale": 0.11,
        "dt": 0.018,
    },
    "lorenz_hot_y": {
        "type": "lorenz",
        "component": "y",
        "sigma": 10.0,
        "rho": 28.0,
        "beta": 2.667,
        "scale": 0.08,
        "dt": 0.018,
    },
    "lorenz_hot_z": {
        "type": "lorenz",
        "component": "z",
        "sigma": 10.0,
        "rho": 28.0,
        "beta": 2.667,
        "scale": 0.04,
        "dt": 0.018,
    },
    "lorenz_x": {
        "type": "lorenz",
        "component": "x",
        "sigma": 10.0,
        "rho": 28.0,
        "beta": 2.667,
        "scale": 0.1,
        "dt": 0.01,
    },
    "lorenz_y": {
        "type": "lorenz",
        "component": "y",
        "sigma": 10.0,
        "rho": 28.0,
        "beta": 2.667,
        "scale": 0.1,
        "dt": 0.01,
    },
    "lorenz_z": {
        "type": "lorenz",
        "component": "z",
        "sigma": 10.0,
        "rho": 28.0,
        "beta": 2.667,
        "scale": 0.1,
        "dt": 0.01,
    },
    "duffing_snap_x": {
        "type": "duffing",
        "component": "x",
        "delta": 0.18,
        "alpha": -1.0,
        "beta": 1.0,
        "gamma": 0.46,
        "omega": 1.15,
        "dt": 0.07,
        "scale": 1.6,
    },
    "duffing_snap_v": {
        "type": "duffing",
        "component": "v",
        "delta": 0.18,
        "alpha": -1.0,
        "beta": 1.0,
        "gamma": 0.46,
        "omega": 1.15,
        "dt": 0.07,
        "scale": 1.1,
    },
    "duffing_grind_x": {
        "type": "duffing",
        "component": "x",
        "delta": 0.08,
        "alpha": -1.0,
        "beta": 1.0,
        "gamma": 0.62,
        "omega": 1.38,
        "dt": 0.09,
        "scale": 1.8,
    },
    "henon_x": {
        "type": "henon",
        "component": "x",
        "a": 1.4,
        "b": 0.3,
        "scale": 1.25,
    },
    "henon_y": {
        "type": "henon",
        "component": "y",
        "a": 1.4,
        "b": 0.3,
        "scale": 2.8,
    },
    "ikeda_x": {
        "type": "ikeda",
        "component": "x",
        "u": 0.93,
        "scale": 0.9,
    },
    "ikeda_y": {
        "type": "ikeda",
        "component": "y",
        "u": 0.93,
        "scale": 0.9,
    },
    "lattice_energy": {
        "type": "logistic_lattice",
        "n_cells": 192,
        "r": 3.94,
        "coupling": 0.22,
        "substeps": 12,
        "statistic": "energy",
        "scale": 8.0,
    },
    "lattice_gradient": {
        "type": "logistic_lattice",
        "n_cells": 192,
        "r": 3.97,
        "coupling": 0.16,
        "substeps": 16,
        "statistic": "gradient",
        "scale": 9.0,
    },
    "lattice_cell": {
        "type": "logistic_lattice",
        "n_cells": 192,
        "r": 3.91,
        "coupling": 0.08,
        "substeps": 10,
        "statistic": "cell",
        "cell": 37,
        "scale": 5.5,
    },
    "reaction_spot": {
        "type": "reaction_diffusion",
        "n_cells": 256,
        "substeps": 18,
        "feed": 0.0367,
        "kill": 0.0649,
        "statistic": "spot",
        "cell": 97,
        "scale": 11.0,
    },
    "reaction_edge": {
        "type": "reaction_diffusion",
        "n_cells": 256,
        "substeps": 18,
        "feed": 0.029,
        "kill": 0.057,
        "statistic": "edge",
        "scale": 13.0,
    },
    "reaction_centroid": {
        "type": "reaction_diffusion",
        "n_cells": 256,
        "substeps": 20,
        "feed": 0.025,
        "kill": 0.055,
        "statistic": "centroid",
        "scale": 0.09,
    },
    "osc_cloud": {
        "type": "oscillator_bank",
        "n_oscillators": 96,
        "min_freq_hz": 0.01,
        "max_freq_hz": 3.5,
        "fm_depth": 0.7,
        "feedback": 0.12,
        "scale": 2.2,
    },
    "osc_swarm": {
        "type": "oscillator_bank",
        "n_oscillators": 192,
        "min_freq_hz": 0.02,
        "max_freq_hz": 6.0,
        "fm_depth": 1.25,
        "feedback": 0.22,
        "scale": 2.6,
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
    "brown_huge": {
        "type": "brownian",
        "sigma": 0.45,
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
    "sine_sub": {
        "type": "sine",
        "freq_hz": 0.08,
        "amplitude": 2.6,
        "phase": 0.0,
    },
    "sine_med": {
        "type": "sine",
        "freq_hz": 0.3,
        "amplitude": 1.5,
        "phase": 0.0,
    },
    "sine_wide": {
        "type": "sine",
        "freq_hz": 0.45,
        "amplitude": 2.6,
        "phase": 1.5708,
    },
    "sine_fast": {
        "type": "sine",
        "freq_hz": 1.2,
        "amplitude": 2.4,
        "phase": 0.7854,
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
    "pulse_gate": {
        "type": "pulse",
        "rate_hz": 0.35,
        "duty": 0.5,
        "amplitude": 2.4,
    },
    "pulse_slam": {
        "type": "pulse",
        "rate_hz": 0.8,
        "duty": 0.35,
        "amplitude": 2.8,
    },
    "pulse_strobe": {
        "type": "pulse",
        "rate_hz": 2.4,
        "duty": 0.15,
        "amplitude": 2.2,
    },
    "constant_high": {
        "type": "constant",
        "value": 2.5,
    },
    "constant_rail": {
        "type": "constant",
        "value": 3.5,
    },
    "constant_low": {
        "type": "constant",
        "value": -2.5,
    },
    "constant_mid": {
        "type": "constant",
        "value": 1.0,
    },
    "constant_zero": {
        "type": "constant",
        "value": 0.0,
    },
    "random_wide": {
        "type": "random",
        "distribution": "uniform",
        "scale": 2.4,
    },
    "random_hot": {
        "type": "random",
        "distribution": "uniform",
        "scale": 2.4,
    },
}


def _route(pattern):
    return {f"active_{i}": pattern[i % len(pattern)] for i in range(model["n_latents"])}


collections = {
    "coherent_chaos": {
        "description": "sixteen driven axes from related hot Lorenz components",
        "unassigned": "zero",
        "routing": _route(
            [
                ("lorenz_hot_x", 1.0),
                ("lorenz_hot_y", 1.0),
                ("lorenz_hot_z", 1.0),
                ("lorenz_hot_x", -1.0),
                ("lorenz_hot_y", -1.0),
                ("lorenz_hot_z", -1.0),
                ("lorenz_slow", 0.85),
                ("lorenz_slow", -0.85),
            ]
        ),
    },
    "multi_attractor": {
        "description": "lorenz, sine, brownian, and noise sources stacked across all axes",
        "unassigned": "zero",
        "routing": _route(
            [
                ("lorenz_hot_x", 1.0),
                ("lorenz_hot_y", -1.0),
                ("lorenz_hot_z", 1.0),
                ("sine_sub", 1.0),
                ("sine_wide", -1.0),
                ("brown_huge", 1.0),
                ("brown_huge", -1.0),
                ("random_wide", 1.0),
            ]
        ),
    },
    "tension": {
        "description": "moving push-pull axes with rails moved out of the critical first slots",
        "unassigned": "zero",
        "routing": _route(
            [
                ("lorenz_hot_x", 1.0),
                ("lorenz_hot_y", -1.0),
                ("sine_wide", 1.0),
                ("sine_wide", -1.0),
                ("brown_huge", 1.0),
                ("brown_huge", -1.0),
                ("pulse_gate", 1.0),
                ("pulse_gate", -1.0),
                ("lorenz_hot_z", 1.0),
                ("lorenz_hot_z", -1.0),
                ("sine_sub", 1.0),
                ("sine_sub", -1.0),
                ("brown_wide", 0.8),
                ("brown_wide", -0.8),
                ("random_wide", 1.0),
                ("random_wide", -1.0),
            ]
        ),
    },
    "drift": {
        "description": "full-width brownian drift with several clip widths and opposing signs",
        "unassigned": "noise",
        "routing": _route(
            [
                ("brown_huge", 1.0),
                ("brown_huge", -1.0),
                ("brown_wide", 0.3),
                ("brown_wide", -0.3),
                ("brown_narrow", 0.95),
                ("brown_narrow", -0.95),
                ("brown_slow", 1.4),
                ("brown_slow", -1.4),
            ]
        ),
    },
    "pulse": {
        "description": "hard gates mixed with carriers so pulsing does not decode as silence",
        "unassigned": "zero",
        "routing": _route(
            [
                ("pulse_slam", 1.0),
                ("sine_fast", -1.0),
                ("pulse_gate", -1.0),
                ("brown_huge", 1.0),
                ("pulse_strobe", 1.0),
                ("random_wide", -1.0),
                ("sine_fast", 1.0),
                ("lorenz_hot_y", -1.0),
                ("pulse_slam", -1.0),
                ("sine_sub", 1.0),
                ("pulse_gate", 1.0),
                ("brown_huge", -1.0),
                ("pulse_strobe", -1.0),
                ("random_wide", 1.0),
                ("sine_wide", -1.0),
                ("lorenz_hot_x", 1.0),
            ]
        ),
    },
    "scan": {
        "description": "high-amplitude periodic sweep across all active axes",
        "unassigned": "zero",
        "routing": _route(
            [
                ("sine_sub", 1.0),
                ("sine_sub", -1.0),
                ("sine_wide", 1.0),
                ("sine_wide", -1.0),
                ("sine_fast", 1.0),
                ("sine_fast", -1.0),
                ("pulse_slow", 0.45),
                ("pulse_slow", -0.45),
            ]
        ),
    },
    "opposition": {
        "description": "every routed axis has a mirrored partner moving against it",
        "unassigned": "zero",
        "routing": _route(
            [
                ("lorenz_hot_x", 1.0),
                ("lorenz_hot_x", -1.0),
                ("lorenz_hot_y", 1.0),
                ("lorenz_hot_y", -1.0),
                ("brown_huge", 1.0),
                ("brown_huge", -1.0),
                ("pulse_slam", 1.0),
                ("pulse_slam", -1.0),
            ]
        ),
    },
    "outside": {
        "description": "edge-of-range pressure without leaving the observed latent range",
        "unassigned": "zero",
        "routing": _route(
            [
                ("constant_mid", 0.95),
                ("constant_mid", -0.95),
                ("sine_wide", 1.0),
                ("sine_wide", -1.0),
                ("lorenz_hot_x", 1.0),
                ("lorenz_hot_y", -1.0),
                ("pulse_strobe", 1.0),
                ("random_hot", 1.0),
            ]
        ),
    },
    "strange_maps": {
        "description": "discrete attractor maps and Duffing axes with abrupt mirrored folds",
        "unassigned": "zero",
        "routing": _route(
            [
                ("henon_x", 1.0),
                ("henon_y", -1.0),
                ("ikeda_x", 1.0),
                ("ikeda_y", -1.0),
                ("duffing_snap_x", 1.0),
                ("duffing_snap_v", -1.0),
                ("duffing_grind_x", 1.0),
                ("lorenz_hot_z", -1.0),
            ]
        ),
    },
    "reaction_lattice": {
        "description": "expensive spatial simulations projected into competing latent axes",
        "unassigned": "noise",
        "routing": _route(
            [
                ("reaction_spot", 1.0),
                ("reaction_edge", -1.0),
                ("reaction_centroid", 1.0),
                ("lattice_energy", -1.0),
                ("lattice_gradient", 1.0),
                ("lattice_cell", -1.0),
                ("osc_cloud", 0.75),
                ("osc_swarm", -0.75),
            ]
        ),
    },
    "wild_pressure": {
        "description": "high-cost chaotic sources stacked against fast gates and random carriers",
        "unassigned": "zero",
        "routing": _route(
            [
                ("osc_swarm", 1.0),
                ("reaction_edge", 1.0),
                ("lattice_gradient", -1.0),
                ("duffing_grind_x", -1.0),
                ("ikeda_x", 1.0),
                ("henon_x", -1.0),
                ("pulse_strobe", 0.75),
                ("random_hot", -0.85),
                ("osc_cloud", -1.0),
                ("reaction_spot", -1.0),
                ("lattice_energy", 1.0),
                ("duffing_snap_v", 1.0),
                ("ikeda_y", -1.0),
                ("henon_y", 1.0),
                ("sine_fast", -0.9),
                ("brown_huge", 0.8),
            ]
        ),
    },
}

for collection in collections.values():
    collection["fit_observed"] = "if_needed"
    collection["fit_margin"] = 0.95

batch = [
    "coherent_chaos",
    "multi_attractor",
    "tension",
    "drift",
    "pulse",
    "scan",
    "opposition",
    "outside",
    "strange_maps",
    "reaction_lattice",
    "wild_pressure",
]
