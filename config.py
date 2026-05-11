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

model_voice_multi_b2048_r48000_z11 = {
    "path": "./models/voice_multi_b2048_r48000_z11.ts",
    "n_latents": 11,
}

model_crozzoli_bigensemblesmusic_18d = {
    "path": "./models/crozzoli_bigensemblesmusic_18d.ts",
    "n_latents": 18,
    "sample_rate": 44100,
}

model_birds_dawnchorus_b2048_r48000_z8 = {
    "path": "./models/birds_dawnchorus_b2048_r48000_z8.ts",
    "n_latents": 8,
}

model_birds_motherbird_b2048_r48000_z16 = {
    "path": "./models/birds_motherbird_b2048_r48000_z16.ts",
    "n_latents": 16,
    "sample_rate": 44100,
}

model = {
    "attrs": {},
    "sample_rate": 48000,
    "block_size": 2048,
} | model_birds_motherbird_b2048_r48000_z16

global_config = {
    "output_dir": "./output/",
    "duration": 120.0,
    "seed": 875983256,
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
    "lorenz_slingshot_x": {
        "type": "lorenz",
        "component": "x",
        "sigma": 16.0,
        "rho": 42.0,
        "beta": 1.92,
        "scale": 0.085,
        "dt": 0.009,
    },
    "lorenz_slingshot_y": {
        "type": "lorenz",
        "component": "y",
        "sigma": 16.0,
        "rho": 42.0,
        "beta": 1.92,
        "scale": 0.072,
        "dt": 0.009,
    },
    "lorenz_knife_z": {
        "type": "lorenz",
        "component": "z",
        "sigma": 6.5,
        "rho": 74.0,
        "beta": 2.15,
        "scale": 0.028,
        "dt": 0.006,
    },
    "rossler_razor_x": {
        "type": "rossler",
        "component": "x",
        "a": 0.33,
        "b": 0.12,
        "c": 8.7,
        "dt": 0.065,
        "scale": 0.32,
    },
    "rossler_taffy_y": {
        "type": "rossler",
        "component": "y",
        "a": 0.07,
        "b": 0.34,
        "c": 10.0,
        "dt": 0.05,
        "scale": 0.42,
    },
    "rossler_z_spikes": {
        "type": "rossler",
        "component": "z",
        "a": 0.2,
        "b": 0.2,
        "c": 14.0,
        "dt": 0.038,
        "scale": 0.24,
    },
    "duffing_impact_x": {
        "type": "duffing",
        "component": "x",
        "delta": 0.045,
        "alpha": -1.4,
        "beta": 1.18,
        "gamma": 0.88,
        "omega": 1.67,
        "dt": 0.105,
        "scale": 1.9,
    },
    "duffing_impact_v": {
        "type": "duffing",
        "component": "v",
        "delta": 0.045,
        "alpha": -1.4,
        "beta": 1.18,
        "gamma": 0.88,
        "omega": 1.67,
        "dt": 0.105,
        "scale": 1.35,
    },
    "duffing_broken_spring": {
        "type": "duffing",
        "component": "x",
        "delta": 0.28,
        "alpha": -0.38,
        "beta": 0.44,
        "gamma": 0.93,
        "omega": 0.71,
        "dt": 0.058,
        "scale": 2.25,
    },
    "henon_shards_x": {
        "type": "henon",
        "component": "x",
        "a": 1.365,
        "b": 0.287,
        "scale": 1.9,
    },
    "henon_shards_y": {
        "type": "henon",
        "component": "y",
        "a": 1.365,
        "b": 0.287,
        "scale": 4.4,
    },
    "ikeda_fold_x": {
        "type": "ikeda",
        "component": "x",
        "u": 0.965,
        "scale": 0.72,
    },
    "ikeda_fold_y": {
        "type": "ikeda",
        "component": "y",
        "u": 0.965,
        "scale": 1.25,
    },
    "standard_map_sin": {
        "type": "standard_map",
        "component": "sin",
        "k": 7.8,
        "drift": 0.047,
        "scale": 3.1,
    },
    "standard_map_momentum": {
        "type": "standard_map",
        "component": "momentum",
        "k": 11.4,
        "drift": -0.019,
        "scale": 3.6,
    },
    "lattice_boiling_energy": {
        "type": "logistic_lattice",
        "n_cells": 384,
        "r": 3.995,
        "coupling": 0.31,
        "substeps": 28,
        "statistic": "energy",
        "scale": 3.7,
    },
    "lattice_torn_gradient": {
        "type": "logistic_lattice",
        "n_cells": 512,
        "r": 3.88,
        "coupling": 0.045,
        "substeps": 40,
        "statistic": "gradient",
        "scale": 4.2,
    },
    "lattice_single_spark": {
        "type": "logistic_lattice",
        "n_cells": 257,
        "r": 3.999,
        "coupling": 0.11,
        "substeps": 19,
        "statistic": "cell",
        "cell": 173,
        "scale": 5.8,
    },
    "reaction_worm_mass": {
        "type": "reaction_diffusion",
        "n_cells": 384,
        "substeps": 42,
        "feed": 0.018,
        "kill": 0.051,
        "statistic": "mass",
        "scale": 3.2,
    },
    "reaction_lace_edge": {
        "type": "reaction_diffusion",
        "n_cells": 384,
        "substeps": 36,
        "feed": 0.044,
        "kill": 0.063,
        "statistic": "edge",
        "scale": 4.6,
    },
    "reaction_anchor_centroid": {
        "type": "reaction_diffusion",
        "n_cells": 320,
        "substeps": 48,
        "feed": 0.026,
        "kill": 0.054,
        "statistic": "centroid",
        "scale": 2.8,
    },
    "ca_rule30_edge": {
        "type": "cellular_automaton",
        "rule": 30,
        "n_cells": 383,
        "substeps": 7,
        "statistic": "edge",
        "scale": 3.4,
    },
    "ca_rule110_window": {
        "type": "cellular_automaton",
        "rule": 110,
        "n_cells": 509,
        "substeps": 13,
        "statistic": "window",
        "scale": 3.0,
    },
    "ca_rule45_cell": {
        "type": "cellular_automaton",
        "rule": 45,
        "n_cells": 257,
        "substeps": 5,
        "statistic": "cell",
        "cell": 91,
        "scale": 2.7,
    },
    "oscillator_hive": {
        "type": "oscillator_bank",
        "n_oscillators": 384,
        "min_freq_hz": 0.006,
        "max_freq_hz": 8.5,
        "fm_depth": 1.75,
        "feedback": 0.36,
        "scale": 3.2,
    },
    "oscillator_glass": {
        "type": "oscillator_bank",
        "n_oscillators": 144,
        "min_freq_hz": 0.0015,
        "max_freq_hz": 1.4,
        "fm_depth": 2.6,
        "feedback": -0.24,
        "scale": 2.9,
    },
    "brownian_cliff": {
        "type": "brownian",
        "sigma": 0.92,
        "clip": [-5.0, 5.0],
    },
    "brownian_molasses": {
        "type": "brownian",
        "sigma": 0.0035,
        "clip": [-1.0, 1.0],
    },
    "sine_subtectonic": {
        "type": "sine",
        "freq_hz": 0.008,
        "amplitude": 4.8,
        "phase": 2.31,
    },
    "sine_slicer": {
        "type": "sine",
        "freq_hz": 3.7,
        "amplitude": 3.6,
        "phase": 0.37,
    },
    "pulse_pinprick": {
        "type": "pulse",
        "rate_hz": 5.2,
        "duty": 0.045,
        "amplitude": 5.0,
    },
    "pulse_breath_hold": {
        "type": "pulse",
        "rate_hz": 0.023,
        "duty": 0.73,
        "amplitude": 4.2,
    },
    "random_gauss_blast": {
        "type": "random",
        "distribution": "normal",
        "scale": 3.1,
    },
    "random_uniform_static": {
        "type": "random",
        "distribution": "uniform",
        "scale": 4.7,
    },
    "constant_ceiling": {
        "type": "constant",
        "value": 6.0,
    },
    "constant_floor": {
        "type": "constant",
        "value": -6.0,
    },
    "constant_zero": {
        "type": "constant",
        "value": 0.0,
    },
}


def _route(pattern):
    return {f"active_{i}": pattern[i % len(pattern)] for i in range(model["n_latents"])}


collections = {
    "violent_attractors": {
        "description": "continuous and discrete attractors pulling against unrelated axes",
        "unassigned": "zero",
        "routing": _route(
            [
                ("lorenz_slingshot_x", 1.0),
                ("rossler_z_spikes", -1.0),
                ("duffing_impact_v", 1.0),
                ("standard_map_momentum", -1.0),
                ("henon_shards_x", 0.9),
                ("ikeda_fold_y", -0.9),
                ("lorenz_knife_z", 1.0),
                ("rossler_razor_x", -1.0),
            ]
        ),
    },
    "cellular_weather": {
        "description": "cellular automata, reaction diffusion, and map lattices as moving weather",
        "unassigned": "noise",
        "routing": _route(
            [
                ("ca_rule30_edge", 1.0),
                ("ca_rule110_window", -1.0),
                ("reaction_worm_mass", 1.0),
                ("reaction_lace_edge", -1.0),
                ("lattice_boiling_energy", 1.0),
                ("lattice_torn_gradient", -1.0),
                ("ca_rule45_cell", 0.85),
                ("reaction_anchor_centroid", -0.85),
            ]
        ),
    },
    "event_horizon": {
        "description": "slow rails and brownian cliffs interrupted by pinprick gates",
        "unassigned": "zero",
        "routing": _route(
            [
                ("constant_ceiling", 1.0),
                ("constant_floor", 1.0),
                ("sine_subtectonic", 1.0),
                ("brownian_cliff", -1.0),
                ("pulse_pinprick", 1.0),
                ("pulse_breath_hold", -1.0),
                ("random_gauss_blast", 0.75),
                ("oscillator_glass", -0.8),
            ]
        ),
    },
    "glass_insects": {
        "description": "dense beating oscillator swarms crossed with high-rate slicers",
        "unassigned": "zero",
        "routing": _route(
            [
                ("oscillator_hive", 1.0),
                ("oscillator_glass", -1.0),
                ("sine_slicer", 1.0),
                ("standard_map_sin", -1.0),
                ("pulse_pinprick", 0.75),
                ("random_uniform_static", -0.65),
                ("duffing_broken_spring", 1.0),
                ("brownian_molasses", -1.8),
            ]
        ),
    },
    "pressure_cooker": {
        "description": "every family represented with mismatched polarity and time scale",
        "unassigned": "noise",
        "routing": _route(
            [
                ("reaction_lace_edge", 1.0),
                ("lorenz_slingshot_y", -1.0),
                ("oscillator_hive", 0.9),
                ("lattice_single_spark", -0.9),
                ("henon_shards_y", 0.75),
                ("rossler_taffy_y", -0.85),
                ("ca_rule30_edge", 1.0),
                ("duffing_impact_x", -1.0),
                ("standard_map_momentum", 0.8),
                ("ikeda_fold_x", -1.0),
                ("sine_subtectonic", 0.65),
                ("pulse_breath_hold", -0.65),
                ("random_gauss_blast", 0.55),
                ("reaction_anchor_centroid", -0.8),
                ("lorenz_knife_z", 1.0),
                ("oscillator_glass", -0.9),
            ]
        ),
    },
    "hard_switchboard": {
        "description": "mostly discontinuous or near-discontinuous control surfaces",
        "unassigned": "zero",
        "routing": _route(
            [
                ("pulse_pinprick", 1.0),
                ("ca_rule45_cell", -1.0),
                ("standard_map_sin", 1.0),
                ("random_uniform_static", -1.0),
                ("constant_ceiling", 0.8),
                ("constant_floor", 0.8),
                ("lattice_single_spark", 1.0),
                ("sine_slicer", -1.0),
            ]
        ),
    },
}

for collection in collections.values():
    collection["fit_observed"] = "if_needed"
    collection["fit_margin"] = 0.95

batch = [
    "violent_attractors",
    "cellular_weather",
    "event_horizon",
    "glass_insects",
    "pressure_cooker",
    "hard_switchboard",
]
