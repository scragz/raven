# Raven 🐦‍⬛: RAVE Latent Trajectory Generator

## Purpose

Generate batches of WAV files by feeding designed latent vector trajectories into a pretrained RAVE decoder. No encoder usage, no realtime output. Raw material for further processing.

## Python package layout

Raven uses a modern `src/` layout. Runtime code lives in the `raven` package under `src/raven`, and the CLI entry point is exposed as `raven`.

```bash
python -m pip install -e .
raven [config.py] [--debug]
```

You can also run the package module directly during development:

```bash
PYTHONPATH=src python -m raven [config.py] [--debug]
```

If no `./config.py` is present, Raven falls back to the bundled default config at `src/raven/config.py`.
