from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass(frozen=True)
class RuntimeConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    max_image_dim: int = 512
    jpeg_quality: int = 85
    max_new_tokens: int = 24
    temperature: float = 0.0
    top_p: float = 1.0
    repetition_penalty: float = 1.0
    preprocess_threads: int = 2
    postprocess_threads: int = 1
    batch_size: int = 1
    warmup_query: str = "the center object"
    model_dir: str = "models/Qwen2-VL-2B-Instruct"
    hailo_hef_path: str = "models/qwen2vl_vision_encoder.hef"
    hailo_postprocess_so: Optional[str] = None
    stop_sequence: str = "]"


def _env_override_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value is not None else default


def _env_override_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value is not None else default


def load_config(path: str = "config.yaml") -> RuntimeConfig:
    raw = {}
    cfg_path = Path(path)
    if cfg_path.exists():
        raw = yaml.safe_load(cfg_path.read_text()) or {}

    return RuntimeConfig(
        host=os.getenv("BBOX_HOST", raw.get("host", RuntimeConfig.host)),
        port=_env_override_int("BBOX_PORT", raw.get("port", RuntimeConfig.port)),
        max_image_dim=_env_override_int(
            "BBOX_MAX_IMAGE_DIM", raw.get("max_image_dim", RuntimeConfig.max_image_dim)
        ),
        jpeg_quality=_env_override_int(
            "BBOX_JPEG_QUALITY", raw.get("jpeg_quality", RuntimeConfig.jpeg_quality)
        ),
        max_new_tokens=_env_override_int(
            "BBOX_MAX_NEW_TOKENS", raw.get("max_new_tokens", RuntimeConfig.max_new_tokens)
        ),
        temperature=_env_override_float(
            "BBOX_TEMPERATURE", raw.get("temperature", RuntimeConfig.temperature)
        ),
        top_p=_env_override_float("BBOX_TOP_P", raw.get("top_p", RuntimeConfig.top_p)),
        repetition_penalty=_env_override_float(
            "BBOX_REPETITION_PENALTY",
            raw.get("repetition_penalty", RuntimeConfig.repetition_penalty),
        ),
        preprocess_threads=_env_override_int(
            "BBOX_PREPROCESS_THREADS",
            raw.get("preprocess_threads", RuntimeConfig.preprocess_threads),
        ),
        postprocess_threads=_env_override_int(
            "BBOX_POSTPROCESS_THREADS",
            raw.get("postprocess_threads", RuntimeConfig.postprocess_threads),
        ),
        batch_size=_env_override_int("BBOX_BATCH_SIZE", raw.get("batch_size", 1)),
        warmup_query=os.getenv("BBOX_WARMUP_QUERY", raw.get("warmup_query", RuntimeConfig.warmup_query)),
        model_dir=os.getenv("BBOX_MODEL_DIR", raw.get("model_dir", RuntimeConfig.model_dir)),
        hailo_hef_path=os.getenv(
            "BBOX_HAILO_HEF_PATH", raw.get("hailo_hef_path", RuntimeConfig.hailo_hef_path)
        ),
        hailo_postprocess_so=os.getenv(
            "BBOX_HAILO_POSTPROCESS_SO",
            raw.get("hailo_postprocess_so", RuntimeConfig.hailo_postprocess_so),
        ),
        stop_sequence=os.getenv("BBOX_STOP_SEQUENCE", raw.get("stop_sequence", RuntimeConfig.stop_sequence)),
    )
