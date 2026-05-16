# ---------------------------------------------------------------------------
# Model selection
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Global config
# ---------------------------------------------------------------------------

global_config = {
    "output_dir": "./output/",
    "duration": 120.0,
    "seed": 875983256,
    "normalize": True,
}

# ---------------------------------------------------------------------------
# Sweep config
# ---------------------------------------------------------------------------

sweep = {
    "enabled": True,
    "cache": True,
    "range": [-3.0, 3.0],
    "steps": 100,
    "threshold": 1e-6,
    # Weight for timbral (spectral centroid) variance in the combined ranking score.
    # Increase to surface dims that strongly modulate timbre without changing loudness.
    "timbral_weight": 0.2,
}

# ---------------------------------------------------------------------------
# Sources
#
# Each source generates one trajectory (n_steps,).  Sources are named and
# generated once per run; multiple dims that reference the same source name
# share the same trajectory and are therefore correlated.
#
# Design convention:
#   - All stochastic/chaotic sources output approximately ±1.0 at scale=1.0.
#   - Routing gains are the amplitude knob (gain=2.0 → ±2.0 in latent space).
#   - Analytic sources (sine, pulse, constant) output at face-value amplitude.
#
# Tier labels in comments describe intended use in the routing hierarchy:
#   MACRO  — active_0, active_1  (slow, deep: the broad compositional arc)
#   MESO   — active_2–5          (medium drift: correlated texture motion)
#   MICRO  — active_6+           (subtle: shimmer and breathe without losing identity)
# ---------------------------------------------------------------------------

sources = {
    # -----------------------------------------------------------------------
    # MACRO — slow mean-reverting walks, deep range
    # theta=0.02 → time constant ≈ 50 s at 23.4 Hz latent rate
    # steady-state std ≈ sigma / sqrt(2·theta)
    # -----------------------------------------------------------------------
    "macro_ou_a": {
        "type": "ornstein_uhlenbeck",
        "theta": 0.02,
        "sigma": 0.20,   # steady-state std ≈ 1.0
        "mu": 0.0,
        "scale": 1.0,
    },
    "macro_ou_b": {
        "type": "ornstein_uhlenbeck",
        "theta": 0.015,  # even slower
        "sigma": 0.17,   # steady-state std ≈ 1.0
        "mu": 0.0,
        "scale": 1.0,
    },
    "macro_sine": {
        "type": "sine",
        "freq_hz": 0.005,
        "amplitude": 1.0,
        "phase": 0.0,
    },
    # Lorenz at a leisurely dt — good for large, sweeping macro arcs
    "macro_lorenz_x": {
        "type": "lorenz",
        "component": "x",
        "sigma": 10.0,
        "rho": 28.0,
        "beta": 2.667,
        "scale": 1.0,
        "dt": 0.012,
    },
    "macro_lorenz_z": {
        "type": "lorenz",
        "component": "z",
        "sigma": 10.0,
        "rho": 28.0,
        "beta": 2.667,
        "scale": 1.0,
        "dt": 0.012,
    },

    # -----------------------------------------------------------------------
    # MESO — medium-speed drift, for correlated texture pairs
    # theta=0.10 → time constant ≈ 10 s; steady-state std ≈ 0.6–0.7
    # -----------------------------------------------------------------------
    "meso_ou_a": {
        "type": "ornstein_uhlenbeck",
        "theta": 0.10,
        "sigma": 0.19,   # steady-state std ≈ 0.6
        "mu": 0.0,
        "scale": 1.0,
    },
    "meso_ou_b": {
        "type": "ornstein_uhlenbeck",
        "theta": 0.08,
        "sigma": 0.16,   # steady-state std ≈ 0.57
        "mu": 0.0,
        "scale": 1.0,
    },
    "meso_pink_a": {
        "type": "pink_noise",
        "scale": 1.0,
    },
    "meso_rossler_x": {
        "type": "rossler",
        "component": "x",
        "a": 0.2,
        "b": 0.2,
        "c": 5.7,
        "dt": 0.055,
        "scale": 1.0,
    },
    "meso_rossler_y": {
        "type": "rossler",
        "component": "y",
        "a": 0.2,
        "b": 0.2,
        "c": 5.7,
        "dt": 0.055,
        "scale": 1.0,
    },

    # -----------------------------------------------------------------------
    # MICRO — slow LFOs and subtle drift, ±0.5–1.0 range
    # Use gain ≤ 1.0 in routing to keep these below tonal-identity threshold
    # -----------------------------------------------------------------------
    "micro_lfo_a": {
        "type": "sine",
        "freq_hz": 0.07,
        "amplitude": 1.0,
        "phase": 0.0,
    },
    "micro_lfo_b": {
        "type": "sine",
        "freq_hz": 0.11,
        "amplitude": 1.0,
        "phase": 1.23,
    },
    "micro_lfo_c": {
        "type": "sine",
        "freq_hz": 0.04,
        "amplitude": 1.0,
        "phase": 2.47,
    },
    "micro_lfo_d": {
        "type": "sine",
        "freq_hz": 0.18,
        "amplitude": 1.0,
        "phase": 0.85,
    },
    "micro_ou": {
        "type": "ornstein_uhlenbeck",
        "theta": 0.30,
        "sigma": 0.26,   # steady-state std ≈ 0.43
        "mu": 0.0,
        "scale": 1.0,
    },

    # -----------------------------------------------------------------------
    # CHAOS — strange attractors, normalised to ±1.0
    # These are shared across collections; identical names → same trajectory.
    # -----------------------------------------------------------------------
    "chaos_lorenz_x": {
        "type": "lorenz",
        "component": "x",
        "sigma": 16.0,
        "rho": 42.0,
        "beta": 1.92,
        "scale": 1.0,
        "dt": 0.009,
    },
    "chaos_lorenz_y": {
        "type": "lorenz",
        "component": "y",
        "sigma": 16.0,
        "rho": 42.0,
        "beta": 1.92,
        "scale": 1.0,
        "dt": 0.009,
    },
    "chaos_lorenz_z": {
        "type": "lorenz",
        "component": "z",
        "sigma": 6.5,
        "rho": 74.0,
        "beta": 2.15,
        "scale": 1.0,
        "dt": 0.006,
    },
    "chaos_rossler_x": {
        "type": "rossler",
        "component": "x",
        "a": 0.33,
        "b": 0.12,
        "c": 8.7,
        "dt": 0.065,
        "scale": 1.0,
    },
    "chaos_rossler_y": {
        "type": "rossler",
        "component": "y",
        "a": 0.07,
        "b": 0.34,
        "c": 10.0,
        "dt": 0.05,
        "scale": 1.0,
    },
    "chaos_rossler_z": {
        "type": "rossler",
        "component": "z",
        "a": 0.2,
        "b": 0.2,
        "c": 14.0,
        "dt": 0.038,
        "scale": 1.0,
    },
    "chaos_duffing_x": {
        "type": "duffing",
        "component": "x",
        "delta": 0.045,
        "alpha": -1.4,
        "beta": 1.18,
        "gamma": 0.88,
        "omega": 1.67,
        "dt": 0.105,
        "scale": 1.0,
    },
    "chaos_duffing_v": {
        "type": "duffing",
        "component": "v",
        "delta": 0.045,
        "alpha": -1.4,
        "beta": 1.18,
        "gamma": 0.88,
        "omega": 1.67,
        "dt": 0.105,
        "scale": 1.0,
    },
    "chaos_henon_x": {
        "type": "henon",
        "component": "x",
        "a": 1.365,
        "b": 0.287,
        "scale": 1.0,
    },
    "chaos_henon_y": {
        "type": "henon",
        "component": "y",
        "a": 1.365,
        "b": 0.287,
        "scale": 1.0,
    },
    "chaos_ikeda_x": {
        "type": "ikeda",
        "component": "x",
        "u": 0.965,
        "scale": 1.0,
    },
    "chaos_standard_sin": {
        "type": "standard_map",
        "component": "sin",
        "k": 7.8,
        "drift": 0.047,
        "scale": 1.0,
    },
    "chaos_standard_mom": {
        "type": "standard_map",
        "component": "momentum",
        "k": 11.4,
        "drift": -0.019,
        "scale": 1.0,
    },

    # -----------------------------------------------------------------------
    # TEXTURE — cellular automata, reaction diffusion, lattices
    # -----------------------------------------------------------------------
    "texture_ca_30": {
        "type": "cellular_automaton",
        "rule": 30,
        "n_cells": 383,
        "substeps": 7,
        "statistic": "edge",
        "scale": 1.0,
    },
    "texture_ca_110": {
        "type": "cellular_automaton",
        "rule": 110,
        "n_cells": 509,
        "substeps": 13,
        "statistic": "window",
        "scale": 1.0,
    },
    "texture_ca_45": {
        "type": "cellular_automaton",
        "rule": 45,
        "n_cells": 257,
        "substeps": 5,
        "statistic": "cell",
        "cell": 91,
        "scale": 1.0,
    },
    "texture_rd_mass": {
        "type": "reaction_diffusion",
        "n_cells": 384,
        "substeps": 42,
        "feed": 0.018,
        "kill": 0.051,
        "statistic": "mass",
        "scale": 1.0,
    },
    "texture_rd_edge": {
        "type": "reaction_diffusion",
        "n_cells": 384,
        "substeps": 36,
        "feed": 0.044,
        "kill": 0.063,
        "statistic": "edge",
        "scale": 1.0,
    },
    "texture_rd_centroid": {
        "type": "reaction_diffusion",
        "n_cells": 320,
        "substeps": 48,
        "feed": 0.026,
        "kill": 0.054,
        "statistic": "centroid",
        "scale": 1.0,
    },
    "texture_lattice_energy": {
        "type": "logistic_lattice",
        "n_cells": 384,
        "r": 3.995,
        "coupling": 0.31,
        "substeps": 28,
        "statistic": "energy",
        "scale": 1.0,
    },
    "texture_lattice_gradient": {
        "type": "logistic_lattice",
        "n_cells": 512,
        "r": 3.88,
        "coupling": 0.045,
        "substeps": 40,
        "statistic": "gradient",
        "scale": 1.0,
    },
    "texture_lattice_cell": {
        "type": "logistic_lattice",
        "n_cells": 257,
        "r": 3.999,
        "coupling": 0.11,
        "substeps": 19,
        "statistic": "cell",
        "cell": 173,
        "scale": 1.0,
    },

    # -----------------------------------------------------------------------
    # OSCILLATORS — dense beating clouds
    # -----------------------------------------------------------------------
    "osc_hive": {
        "type": "oscillator_bank",
        "n_oscillators": 384,
        "min_freq_hz": 0.006,
        "max_freq_hz": 8.5,
        "fm_depth": 1.75,
        "feedback": 0.36,
        "scale": 1.0,
    },
    "osc_glass": {
        "type": "oscillator_bank",
        "n_oscillators": 144,
        "min_freq_hz": 0.0015,
        "max_freq_hz": 1.4,
        "fm_depth": 2.6,
        "feedback": -0.24,
        "scale": 1.0,
    },

    # -----------------------------------------------------------------------
    # EVENT — pulses, rails, static
    # -----------------------------------------------------------------------
    "pulse_slow": {
        "type": "pulse",
        "rate_hz": 0.023,
        "duty": 0.73,
        "amplitude": 1.0,
    },
    "pulse_fast": {
        "type": "pulse",
        "rate_hz": 5.2,
        "duty": 0.045,
        "amplitude": 1.0,
    },
    "rail_high": {
        "type": "constant",
        "value": 1.0,
    },
    "rail_low": {
        "type": "constant",
        "value": -1.0,
    },
    "static_normal": {
        "type": "random",
        "distribution": "normal",
        "scale": 1.0,
    },
    "static_uniform": {
        "type": "random",
        "distribution": "uniform",
        "scale": 1.0,
    },
}

# ---------------------------------------------------------------------------
# Collections
#
# Routing structure:
#   "active_N" → list of contribution dicts
#       {"src": source_name, "gain": float, "offset": float, "smooth": float}
#
# active_0, active_1          MACRO tier  — dominant perceptual levers
# active_2 … active_5         MESO tier   — correlated texture drift
# active_6 … active_N         MICRO tier  — shimmer and breathe
#
# Sharing a "src" name across dims produces correlated motion (they ride the
# same generated trajectory, scaled and offset differently).
# "smooth" is an IIR coefficient: 0 = no smoothing, 0.9 ≈ very slow.
# ---------------------------------------------------------------------------

collections = {
    # -----------------------------------------------------------------------
    "slow_morphology": {
        # Pure correlation study.  Both macro dims share macro_ou_a; each
        # meso pair shares its own OU source.  Nothing moves independently.
        "description": "correlated OU drift across all tiers; textbook shared-source co-variation",
        "unassigned": "zero",
        "fit_observed": "if_needed",
        "fit_margin": 0.95,
        "routing": {
            # MACRO — shared source, different gains/offsets
            "active_0": [{"src": "macro_ou_a", "gain": 2.2}],
            "active_1": [{"src": "macro_ou_a", "gain": 1.4, "offset": 0.3}],
            # MESO — two independent OU sources, each spanning two dims
            "active_2": [{"src": "meso_ou_a", "gain": 1.2}],
            "active_3": [{"src": "meso_ou_a", "gain": 0.8, "offset": -0.25}],
            "active_4": [{"src": "meso_ou_b", "gain": 1.0}],
            "active_5": [{"src": "meso_ou_b", "gain": 0.65, "offset": 0.18}],
            # MICRO — non-harmonic LFOs so no regular beating
            "active_6":  [{"src": "micro_lfo_a", "gain": 0.8}],
            "active_7":  [{"src": "micro_lfo_b", "gain": 0.65}],
            "active_8":  [{"src": "micro_lfo_c", "gain": 0.7}],
            "active_9":  [{"src": "micro_ou",    "gain": 0.5}],
            "active_10": [{"src": "micro_lfo_d", "gain": 0.55}],
            "active_11": [{"src": "micro_lfo_a", "gain": 0.4, "offset": 0.1}],
        },
    },

    # -----------------------------------------------------------------------
    "volatile_attractors": {
        # Chaotic attractors with proper tier hierarchy.  Macro dims share the
        # same Lorenz trajectory so the dominant energy arc stays coherent even
        # as lower dims writhe.  Discrete maps appear only in the micro tier
        # where their steppiness is smoothed via IIR before reaching the decoder.
        "description": "shared Lorenz macro arc; Rössler meso pairs; smoothed discrete maps in micro",
        "unassigned": "zero",
        "fit_observed": "if_needed",
        "fit_margin": 0.95,
        "routing": {
            # MACRO — chaos_lorenz_x shared; second dim offset to avoid lockstep
            "active_0": [{"src": "chaos_lorenz_x", "gain": 2.0}],
            "active_1": [{"src": "chaos_lorenz_x", "gain": 1.3, "offset": 0.35}],
            # MESO — Rössler x/y correlated by sharing meso_ou_a as a common
            #         low-level rider underneath the attractor signal
            "active_2": [
                {"src": "chaos_rossler_x", "gain": 1.4},
                {"src": "meso_ou_a",       "gain": 0.35},
            ],
            "active_3": [
                {"src": "chaos_rossler_y", "gain": 1.2},
                {"src": "meso_ou_a",       "gain": 0.25},
            ],
            "active_4": [{"src": "chaos_henon_x", "gain": 1.5}],
            "active_5": [{"src": "chaos_henon_x", "gain": 1.0, "offset": -0.3}],
            # MICRO — discrete maps smoothed so step edges don't click the decoder
            "active_6":  [{"src": "chaos_ikeda_x",   "gain": 1.0, "smooth": 0.65}],
            "active_7":  [{"src": "chaos_duffing_x",  "gain": 0.9, "smooth": 0.50}],
            "active_8":  [{"src": "chaos_lorenz_z",   "gain": 0.85, "smooth": 0.45}],
            "active_9":  [{"src": "micro_lfo_a",      "gain": 0.7}],
            "active_10": [{"src": "chaos_rossler_z",  "gain": 0.75, "smooth": 0.55}],
            "active_11": [{"src": "micro_lfo_b",      "gain": 0.6}],
        },
    },

    # -----------------------------------------------------------------------
    "cellular_weather": {
        # Cellular automata, reaction diffusion, and lattices as the texture
        # layer, but each pair of texture dims is anchored to a shared OU
        # source so they breathe together rather than flailing independently.
        "description": "CA/RD/lattice texture grounded by shared OU anchors per meso pair",
        "unassigned": "noise",
        "fit_observed": "if_needed",
        "fit_margin": 0.95,
        "routing": {
            # MACRO — shared OU defines the weather system's energy envelope
            "active_0": [{"src": "macro_ou_b", "gain": 2.0}],
            "active_1": [{"src": "macro_ou_b", "gain": 1.4, "offset": 0.4}],
            # MESO — texture + shared OU rider keeps each pair correlated
            "active_2": [
                {"src": "texture_ca_30",        "gain": 1.4},
                {"src": "meso_ou_a",            "gain": 0.4},
            ],
            "active_3": [
                {"src": "texture_rd_mass",      "gain": 1.2},
                {"src": "meso_ou_a",            "gain": 0.35},
            ],
            "active_4": [
                {"src": "texture_lattice_energy","gain": 1.1},
                {"src": "meso_ou_b",             "gain": 0.4},
            ],
            "active_5": [
                {"src": "texture_rd_edge",      "gain": 1.3},
                {"src": "meso_ou_b",            "gain": 0.3},
            ],
            # MICRO — smoother CA statistics; IIR tames binary jumps
            "active_6":  [{"src": "texture_ca_110",        "gain": 0.85, "smooth": 0.55}],
            "active_7":  [{"src": "texture_ca_45",         "gain": 0.7,  "smooth": 0.50}],
            "active_8":  [{"src": "texture_lattice_gradient","gain": 0.65, "smooth": 0.60}],
            "active_9":  [{"src": "texture_rd_centroid",   "gain": 0.6,  "smooth": 0.55}],
            "active_10": [{"src": "micro_lfo_a",           "gain": 0.7}],
            "active_11": [{"src": "texture_lattice_cell",  "gain": 0.55, "smooth": 0.65}],
        },
    },

    # -----------------------------------------------------------------------
    "event_horizon": {
        # Macro layer is a very slow sine — the "rail" that defines the
        # overall arc.  Meso dims drift around it via correlated OU.  Pulses
        # appear only in micro, heavily smoothed so they become slow swells
        # rather than clicks.
        "description": "slow sine rail at macro; correlated OU meso drift; smoothed pulse micro swells",
        "unassigned": "zero",
        "fit_observed": "if_needed",
        "fit_margin": 0.95,
        "routing": {
            # MACRO — sine rail + correlated OU gives a guided wander
            "active_0": [
                {"src": "macro_sine",   "gain": 2.5},
                {"src": "macro_ou_a",   "gain": 0.5},
            ],
            "active_1": [
                {"src": "macro_sine",   "gain": 1.8, "offset": 0.4},
                {"src": "macro_ou_a",   "gain": 0.4},
            ],
            # MESO — correlated OU pairs drift around the rail
            "active_2": [{"src": "meso_ou_a", "gain": 1.1}],
            "active_3": [{"src": "meso_ou_a", "gain": 0.75, "offset": 0.2}],
            "active_4": [{"src": "meso_ou_b", "gain": 1.0}],
            "active_5": [{"src": "meso_ou_b", "gain": 0.7, "offset": -0.15}],
            # MICRO — pulses smoothed to slow timbral swells
            "active_6":  [{"src": "pulse_slow", "gain": 1.6,  "smooth": 0.88}],
            "active_7":  [{"src": "pulse_fast", "gain": 0.9,  "smooth": 0.96}],
            "active_8":  [{"src": "micro_lfo_a","gain": 0.75}],
            "active_9":  [{"src": "micro_lfo_c","gain": 0.65}],
            "active_10": [{"src": "micro_ou",   "gain": 0.5}],
            "active_11": [{"src": "micro_lfo_b","gain": 0.55}],
        },
    },

    # -----------------------------------------------------------------------
    "glass_insects": {
        # Macro dims share the hive oscillator bank — the swarm's energy
        # envelope — while meso dims layer the glass bank with correlated OU
        # drift.  Pink noise in meso adds non-periodic variation.
        "description": "shared oscillator-bank macro envelope; osc_glass + OU meso; LFO micro shimmer",
        "unassigned": "zero",
        "fit_observed": "if_needed",
        "fit_margin": 0.95,
        "routing": {
            # MACRO — shared hive swarm, offset second dim for slight independence
            "active_0": [{"src": "osc_hive", "gain": 2.1}],
            "active_1": [{"src": "osc_hive", "gain": 1.4, "offset": 0.3}],
            # MESO — glass bank correlated via shared meso_ou_a rider
            "active_2": [
                {"src": "osc_glass",   "gain": 1.3},
                {"src": "meso_ou_a",   "gain": 0.4},
            ],
            "active_3": [
                {"src": "osc_glass",   "gain": 0.9, "offset": -0.2},
                {"src": "meso_ou_a",   "gain": 0.3},
            ],
            "active_4": [
                {"src": "chaos_standard_sin", "gain": 1.1},
                {"src": "meso_ou_b",          "gain": 0.35},
            ],
            "active_5": [{"src": "meso_pink_a", "gain": 1.0}],
            # MICRO — LFOs with mild smoothing for shimmer without clicking
            "active_6":  [{"src": "micro_lfo_a", "gain": 0.85, "smooth": 0.25}],
            "active_7":  [{"src": "micro_lfo_b", "gain": 0.70}],
            "active_8":  [{"src": "micro_lfo_c", "gain": 0.65}],
            "active_9":  [{"src": "osc_glass",   "gain": 0.55, "smooth": 0.70}],
            "active_10": [{"src": "micro_ou",    "gain": 0.5}],
            "active_11": [{"src": "micro_lfo_d", "gain": 0.45}],
        },
    },

    # -----------------------------------------------------------------------
    "hard_switchboard": {
        # Deliberately ignores the hierarchy and smoothing advice.  Fast pulses,
        # white noise, and constants with no IIR damping — the decoder is pushed
        # to its discontinuity limit.  fit_observed="never" so out-of-range
        # values are not clamped; the glitch is the aesthetic.
        "description": "discontinuous control surfaces; no smoothing; intentional decoder artifacts",
        "unassigned": "zero",
        "fit_observed": "never",
        "fit_margin": 0.95,
        "routing": {
            "active_0": [{"src": "pulse_fast",     "gain": 3.2}],
            "active_1": [{"src": "texture_ca_45",  "gain": 2.8}],
            "active_2": [{"src": "chaos_standard_sin", "gain": 2.6}],
            "active_3": [{"src": "static_uniform",     "gain": 2.2}],
            "active_4": [{"src": "rail_high",          "gain": 2.5}],
            "active_5": [{"src": "rail_low",           "gain": 2.5}],
            "active_6": [{"src": "texture_lattice_cell","gain": 2.3}],
            "active_7": [{"src": "chaos_henon_y",      "gain": 2.1}],
            "active_8": [{"src": "chaos_standard_mom", "gain": 2.0}],
            "active_9": [{"src": "static_normal",      "gain": 1.8}],
            "active_10":[{"src": "pulse_slow",         "gain": 2.4}],
            "active_11":[{"src": "chaos_duffing_v",    "gain": 1.9}],
        },
    },
}

batch = [
    "slow_morphology",
    "volatile_attractors",
    "cellular_weather",
    "event_horizon",
    "glass_insects",
    "hard_switchboard",
]
