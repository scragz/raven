import logging

import numpy as np
import torch

logger = logging.getLogger(__name__)

# Fallback attribute name lists in priority order
_SR_ATTRS = ["sr", "sample_rate"]
_BLOCK_ATTRS = ["block_size", "hop_length"]
_LATENT_ATTRS = ["latent_size", "n_latents", "z_dim", "latent_dim"]


class RAVEModel:
    def __init__(self, model_cfg: dict):
        self.cfg = model_cfg
        self._load()
        self._verify()
        self._apply_attrs()

    def _load(self):
        path = self.cfg["path"]
        logger.info(f"Loading TorchScript model from {path}")
        self.model = torch.jit.load(path, map_location="cpu")
        self.model.eval()

    def _get_attr(self, names: list):
        for name in names:
            try:
                val = getattr(self.model, name)
                if isinstance(val, torch.Tensor):
                    val = int(val.item())
                return int(val)
            except AttributeError:
                continue
        return None

    def _verify(self):
        checks = [
            ("sample_rate", _SR_ATTRS, self.cfg["sample_rate"]),
            ("block_size", _BLOCK_ATTRS, self.cfg["block_size"]),
            ("n_latents", _LATENT_ATTRS, self.cfg["n_latents"]),
        ]
        for label, attr_names, expected in checks:
            actual = self._get_attr(attr_names)
            if actual is None:
                logger.warning(
                    f"Model does not expose {label} attribute "
                    f"(tried: {attr_names}); trusting config value {expected}"
                )
            elif actual != expected:
                raise ValueError(f"Model {label} mismatch: model={actual}, config={expected}")
            else:
                logger.debug(f"  {label}: {actual} ✓")

    def _apply_attrs(self):
        for k, v in self.cfg.get("attrs", {}).items():
            try:
                setattr(self.model, k, v)
                logger.debug(f"  set model.{k} = {v}")
            except Exception as e:
                logger.warning(f"Could not set model.{k}: {e}")

    def decode(self, latent_vector: np.ndarray) -> np.ndarray:
        """Decode one latent frame to one audio block.

        Args:
            latent_vector: shape (n_latents,)

        Returns:
            audio block as float32 array, shape (block_size,)
        """
        z = (
            torch.from_numpy(latent_vector.astype(np.float32))
            .unsqueeze(0)  # (1, n_latents)
            .unsqueeze(-1)  # (1, n_latents, 1)
        )
        with torch.no_grad():
            audio = self.model.decode(z)

        audio = audio.squeeze().cpu().numpy()
        # Normalise shape to (block_size,): handle (1, block_size) or (block_size,)
        if audio.ndim > 1:
            audio = audio[0]
        return audio.astype(np.float32)
