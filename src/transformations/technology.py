"""Canonical technology classification rules for the project."""

from __future__ import annotations

import re
import unicodedata


COMBUSTAO = "COMBUSTAO"
HIBRIDO = "HIBRIDO"
ELETRICO = "ELETRICO"
OUTRO = "OUTRO"
NAO_INFORMADO = "NAO_INFORMADO"

STANDARD_TECHNOLOGIES = (COMBUSTAO, HIBRIDO, ELETRICO, OUTRO, NAO_INFORMADO)
ABVE_ELECTRIFIED_COMPONENTS = {"BEV", "PHEV", "HEV", "HEV FLEX"}


def _normalize(value: str) -> str:
    without_accents = "".join(
        char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char)
    )
    return re.sub(r"\s+", " ", without_accents).strip().upper()


def classify_technology(original_category: str | None) -> str:
    """Map a source category to the project's five canonical classes."""

    if original_category is None or not original_category.strip():
        return NAO_INFORMADO

    value = _normalize(original_category)
    if value in {"BEV", "EV", "ELETRICO", "ELETRICOS", "100% ELETRICO", "100% ELETRICOS"}:
        return ELETRICO
    if value in {
        "PHEV",
        "HEV",
        "HEV FLEX",
        "MHEV",
        "MHEV 12V",
        "MHEV 48V",
        "HIBRIDO",
        "HIBRIDOS",
        "HÍBRIDO",
    }:
        return HIBRIDO
    if value in {
        "FLEX",
        "GASOLINA",
        "DIESEL",
        "ETANOL",
        "GNV",
        "CNG",
        "COMBUSTAO",
        "COMBUSTAO INTERNA",
    }:
        return COMBUSTAO
    if value in {"OUTRO", "OUTROS", "TOTAL", "ELETRIFICADOS", "NAO APLICAVEL"}:
        return OUTRO
    return OUTRO


def is_abve_electrified_component(original_category: str | None) -> bool:
    """Return whether ABVE includes the source category in electrified total."""

    return original_category is not None and _normalize(original_category) in ABVE_ELECTRIFIED_COMPONENTS
