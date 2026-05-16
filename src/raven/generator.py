"""Batch generation pipeline.

For each collection:
    1. Resolve routing (active_N → dim index)
    2. Build latent matrix (n_steps × n_latents)
    3. Decode block by block
    4. Write float32 WAV + JSON sidecar
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import soundfile as sf

from .routing import build_latents, resolve_routing

logger = logging.getLogger(__name__)


def _model_stem(model_path: str) -> str:
    return Path(model_path).stem


def generate_collection(
    model,
    config: dict,
    collection_name: str,
    sweep_cache: dict,
    global_seed: int,
    timestamp: str,
) -> tuple:
    """Generate audio for one collection.

    Returns:
        (wav_path: str, warnings: list[str])
    """
    model_cfg = config["model"]
    global_cfg = config["global_config"]
    collection = config["collections"][collection_name]
    sources_cfg = config["sources"]

    sr = model_cfg["sample_rate"]
    block_size = model_cfg["block_size"]
    n_latents = model_cfg["n_latents"]
    sr_latent = sr / block_size

    n_steps = int(global_cfg["duration"] * sr_latent)
    active_dims = sweep_cache["active_dims"]

    resolved = resolve_routing(collection["routing"], active_dims)

    latents, warnings = build_latents(
        n_steps=n_steps,
        n_latents=n_latents,
        resolved_routing=resolved,
        unassigned_policy=collection["unassigned"],
        sources_cfg=sources_cfg,
        global_seed=global_seed,
        sr_latent=sr_latent,
        sweep_cache=sweep_cache,
        fit_observed=collection.get("fit_observed", False),
        fit_margin=collection.get("fit_margin", 0.95),
    )

    for w in warnings:
        logger.warning(f"[{collection_name}] {w}")

    # Decode loop
    logger.info(f"  Decoding {n_steps} blocks…")
    blocks = []
    for step in range(n_steps):
        block = model.decode(latents[step])
        blocks.append(block)

    audio = np.concatenate(blocks).astype(np.float32)

    if global_cfg.get("normalize", False):
        peak = float(np.max(np.abs(audio)))
        if peak > 0.0:
            audio /= peak

    # Output paths
    out_dir = Path(global_cfg["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    model_name = _model_stem(model_cfg["path"])
    base = f"{timestamp}_{global_seed}_{model_name}_{collection_name}"
    wav_path = out_dir / (base + ".wav")
    json_path = out_dir / (base + ".json")

    sf.write(str(wav_path), audio, sr, subtype="FLOAT")
    logger.info(f"  → {wav_path}")

    # Collect source definitions actually used in this collection
    used_src_names: set[str] = set()
    for contribs in collection["routing"].values():
        for c in contribs:
            used_src_names.add(c["src"])
    sources_used = {
        name: sources_cfg[name] for name in sorted(used_src_names) if name in sources_cfg
    }

    sidecar = {
        "collection_name": collection_name,
        "description": collection.get("description", ""),
        "timestamp": timestamp,
        "seed": global_seed,
        "model": model_cfg,
        "global_config": global_cfg,
        "collection": collection,
        "sources_used": sources_used,
        "active_dims": active_dims,
        "observed_ranges": sweep_cache.get("observed_ranges", {}),
        "rms_variance": sweep_cache.get("rms_variance", {}),
        "timbral_variance": sweep_cache.get("timbral_variance", {}),
        "routing_resolved": {str(dim): contributions for dim, contributions in resolved.items()},
        "warnings": warnings,
    }

    with open(json_path, "w") as f:
        json.dump(sidecar, f, indent=2)

    return str(wav_path), warnings


def run_batch(model, config: dict, sweep_cache: dict, global_seed: int) -> list:
    """Run all collections listed in config['batch'].

    Returns:
        list of {"collection", "wav", "warnings"} dicts
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = []

    for collection_name in config["batch"]:
        logger.info(f"\n=== {collection_name} ===")
        wav_path, warnings = generate_collection(
            model=model,
            config=config,
            collection_name=collection_name,
            sweep_cache=sweep_cache,
            global_seed=global_seed,
            timestamp=timestamp,
        )
        results.append({"collection": collection_name, "wav": wav_path, "warnings": warnings})

    return results
