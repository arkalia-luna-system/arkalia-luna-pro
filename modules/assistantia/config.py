#!/usr/bin/env python3
"""
🧠 AssistantIA - Gestion de configuration typée

Ce module charge la configuration AssistantIA depuis `config/assistantia_config.toml`
et fournit un accès typé avec valeurs par défaut sûres.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.ark_logger import ark_logger
from modules.utils.helpers import load_toml_cached


@dataclass(slots=True)
class AssistantiaMemoriaConfig:
    enabled: bool = True
    max_context_tokens: int = 2048


@dataclass(slots=True)
class AssistantiaSecurityConfig:
    strict_prompt_validation: bool = True
    min_safety_score: float = 0.3


@dataclass(slots=True)
class AssistantiaConfig:
    enabled: bool = True
    enable_feature_x: bool = False
    api_key: str = ""
    default_model: str = "mistral:latest"
    default_temperature: float = 0.7
    log_level: str = "INFO"
    memoria: AssistantiaMemoriaConfig = AssistantiaMemoriaConfig()
    security: AssistantiaSecurityConfig = AssistantiaSecurityConfig()


config_cache: AssistantiaConfig | None = None


def _safe_get_section(raw: dict[str, Any], name: str) -> dict[str, Any]:
    section = raw.get(name)
    return section if isinstance(section, dict) else {}


def load_assistantia_config() -> AssistantiaConfig:
    """
    Charge et met en cache la configuration AssistantIA.
    """

    global config_cache
    if config_cache is not None:
        return config_cache

    config_path = Path("config/assistantia_config.toml")
    if not config_path.exists():
        config_cache = AssistantiaConfig()
        return config_cache

    try:
        raw: dict[str, Any] = load_toml_cached(str(config_path))
        main_cfg = _safe_get_section(raw, "assistantia")
        memoria_cfg = _safe_get_section(main_cfg, "memoria")
        security_cfg = _safe_get_section(main_cfg, "security")

        config_cache = AssistantiaConfig(
            enabled=bool(main_cfg.get("enabled", True)),
            enable_feature_x=bool(main_cfg.get("enable_feature_x", False)),
            api_key=str(main_cfg.get("api_key", "")),
            default_model=str(main_cfg.get("default_model", "mistral:latest")),
            default_temperature=float(main_cfg.get("default_temperature", 0.7)),
            log_level=str(main_cfg.get("log_level", "INFO")),
            memoria=AssistantiaMemoriaConfig(
                enabled=bool(memoria_cfg.get("enabled", True)),
                max_context_tokens=int(memoria_cfg.get("max_context_tokens", 2048)),
            ),
            security=AssistantiaSecurityConfig(
                strict_prompt_validation=bool(
                    security_cfg.get("strict_prompt_validation", True)
                ),
                min_safety_score=float(security_cfg.get("min_safety_score", 0.3)),
            ),
        )
    except Exception as exc:  # pragma: no cover - chemin de repli
        ark_logger.warning(
            f"Erreur chargement assistantia_config.toml: {exc}",
            extra={"arkalia_module": "assistantia"},
        )
        config_cache = AssistantiaConfig()

    return config_cache

