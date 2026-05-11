# Raven 🐦‍⬛: RAVE Latent Trajectory Generator

## Purpose

Generate batches of WAV files by feeding designed latent vector trajectories into a pretrained RAVE decoder. No encoder usage, no realtime output. Raw material for further processing.

 [Intelligent Instruments Lab](https://iil.is/) made a [bunch of models](https://huggingface.co/Intelligent-Instruments-Lab/rave-models) that is an easy way to get started. Put them in the ./models dir and set one up in the `config.py`. Then `uv run raven` to generate wav files.
