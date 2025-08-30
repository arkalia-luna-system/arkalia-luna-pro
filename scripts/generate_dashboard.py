#!/usr/bin/env python3
"""
🌕 Générateur de Dashboard Grafana - Arkalia-LUNA Pro
Crée un dashboard unifié avec toutes les métriques du système
"""

import json
from pathlib import Path
from typing import Any

from core.ark_logger import ark_logger


def create_arkalia_overview_dashboard() -> dict[str, Any]:
    """Crée le dashboard unifié Arkalia-LUNA Pro"""

    dashboard: dict[str, Any] = {
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": "-- Grafana --",
                    "enable": True,
                    "hide": True,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "type": "dashboard",
                }
            ]
        },
        "description": "🌕 Dashboard Unifié Arkalia-LUNA Pro - Vue d'ensemble complète du système",
        "editable": True,
        "gnetId": None,
        "graphTooltip": 0,
        "id": None,
        "links": [],
        "panels": [
            # Panel 1: Uptime Système
            {
                "datasource": "prometheus",
                "description": "État général du système Arkalia-LUNA",
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "thresholds"},
                        "mappings": [],
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "red", "value": None},
                                {"color": "green", "value": 1},
                            ],
                        },
                    },
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
                "id": 1,
                "options": {
                    "colorMode": "value",
                    "graphMode": "area",
                    "justifyMode": "auto",
                    "orientation": "auto",
                    "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
                    "textMode": "auto",
                },
                "pluginVersion": "10.0.0",
                "targets": [
                    {
                        "expr": "arkalia_system_uptime_seconds",
                        "interval": "",
                        "legendFormat": "Uptime",
                        "refId": "A",
                    }
                ],
                "title": "🕐 Uptime Système",
                "type": "stat",
            },
            # Panel 2: CPU/RAM
            {
                "datasource": "prometheus",
                "description": "Utilisation CPU et RAM en temps réel",
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "palette-classic"},
                        "custom": {
                            "axisLabel": "",
                            "axisPlacement": "auto",
                            "barAlignment": 0,
                            "drawStyle": "line",
                            "fillOpacity": 10,
                            "gradientMode": "none",
                            "hideFrom": {"legend": False, "tooltip": False, "vis": False},
                            "lineInterpolation": "linear",
                            "lineWidth": 2,
                            "pointSize": 5,
                            "scaleDistribution": {"type": "linear"},
                            "showPoints": "never",
                            "spanNulls": False,
                            "stacking": {"group": "A", "mode": "none"},
                            "thresholdsStyle": {"mode": "off"},
                        },
                        "mappings": [],
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "green", "value": None},
                                {"color": "yellow", "value": 70},
                                {"color": "red", "value": 90},
                            ],
                        },
                        "unit": "percent",
                    },
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 9, "x": 6, "y": 0},
                "id": 2,
                "options": {
                    "legend": {"calcs": [], "displayMode": "list", "placement": "bottom"},
                    "tooltip": {"mode": "single"},
                },
                "targets": [
                    {
                        "expr": "arkalia_reflexia_cpu_usage_percent",
                        "interval": "",
                        "legendFormat": "CPU %",
                        "refId": "A",
                    },
                    {
                        "expr": "arkalia_reflexia_ram_usage_percent",
                        "interval": "",
                        "legendFormat": "RAM %",
                        "refId": "B",
                    },
                ],
                "title": "💻 Utilisation CPU/RAM",
                "type": "timeseries",
            },
            # Panel 3: Latence
            {
                "datasource": "prometheus",
                "description": "Latence système et temps de réponse",
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "palette-classic"},
                        "custom": {
                            "axisLabel": "",
                            "axisPlacement": "auto",
                            "barAlignment": 0,
                            "drawStyle": "line",
                            "fillOpacity": 10,
                            "gradientMode": "none",
                            "hideFrom": {"legend": False, "tooltip": False, "vis": False},
                            "lineInterpolation": "linear",
                            "lineWidth": 2,
                            "pointSize": 5,
                            "scaleDistribution": {"type": "linear"},
                            "showPoints": "never",
                            "spanNulls": False,
                            "stacking": {"group": "A", "mode": "none"},
                            "thresholdsStyle": {"mode": "off"},
                        },
                        "mappings": [],
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "green", "value": None},
                                {"color": "yellow", "value": 100},
                                {"color": "red", "value": 500},
                            ],
                        },
                        "unit": "ms",
                    },
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 9, "x": 15, "y": 0},
                "id": 3,
                "options": {
                    "legend": {"calcs": [], "displayMode": "list", "placement": "bottom"},
                    "tooltip": {"mode": "single"},
                },
                "targets": [
                    {
                        "expr": "arkalia_reflexia_latency_ms",
                        "interval": "",
                        "legendFormat": "Latence Système",
                        "refId": "A",
                    },
                    {
                        "expr": "histogram_quantile(0.95, rate(arkalia_assistantia_response_time_seconds_bucket[5m])) * 1000",
                        "interval": "",
                        "legendFormat": "Temps Réponse AssistantIA (95e percentile)",
                        "refId": "B",
                    },
                ],
                "title": "⚡ Latence & Temps de Réponse",
                "type": "timeseries",
            },
            # Panel 4: Décisions ZeroIA
            {
                "datasource": "prometheus",
                "description": "Décisions ZeroIA par minute",
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "palette-classic"},
                        "custom": {
                            "axisLabel": "",
                            "axisPlacement": "auto",
                            "barAlignment": 0,
                            "drawStyle": "line",
                            "fillOpacity": 10,
                            "gradientMode": "none",
                            "hideFrom": {"legend": False, "tooltip": False, "vis": False},
                            "lineInterpolation": "linear",
                            "lineWidth": 2,
                            "pointSize": 5,
                            "scaleDistribution": {"type": "linear"},
                            "showPoints": "never",
                            "spanNulls": False,
                            "stacking": {"group": "A", "mode": "none"},
                            "thresholdsStyle": {"mode": "off"},
                        },
                        "mappings": [],
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [{"color": "green", "value": None}],
                        },
                        "unit": "reqps",
                    },
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                "id": 4,
                "options": {
                    "legend": {"calcs": [], "displayMode": "list", "placement": "bottom"},
                    "tooltip": {"mode": "single"},
                },
                "targets": [
                    {
                        "expr": "rate(arkalia_zeroia_decisions_total[1m])",
                        "interval": "",
                        "legendFormat": "Décisions/min",
                        "refId": "A",
                    }
                ],
                "title": "🧠 Décisions ZeroIA/min",
                "type": "timeseries",
            },
            # Panel 5: Score de Confiance
            {
                "datasource": "prometheus",
                "description": "Score de confiance des décisions ZeroIA",
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "thresholds"},
                        "mappings": [],
                        "max": 1,
                        "min": 0,
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "red", "value": None},
                                {"color": "yellow", "value": 0.3},
                                {"color": "green", "value": 0.7},
                            ],
                        },
                        "unit": "percentunit",
                    },
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                "id": 5,
                "options": {
                    "orientation": "auto",
                    "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
                    "showThresholdLabels": False,
                    "showThresholdMarkers": True,
                },
                "pluginVersion": "10.0.0",
                "targets": [
                    {
                        "expr": "arkalia_zeroia_confidence_score",
                        "interval": "",
                        "legendFormat": "Confiance",
                        "refId": "A",
                    }
                ],
                "title": "🎯 Score de Confiance ZeroIA",
                "type": "gauge",
            },
            # Panel 6: Prompts AssistantIA
            {
                "datasource": "prometheus",
                "description": "Prompts traités par AssistantIA et blocages de sécurité",
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "palette-classic"},
                        "custom": {
                            "axisLabel": "",
                            "axisPlacement": "auto",
                            "barAlignment": 0,
                            "drawStyle": "bars",
                            "fillOpacity": 80,
                            "gradientMode": "none",
                            "hideFrom": {"legend": False, "tooltip": False, "vis": False},
                            "lineInterpolation": "linear",
                            "lineWidth": 1,
                            "pointSize": 5,
                            "scaleDistribution": {"type": "linear"},
                            "showPoints": "never",
                            "spanNulls": False,
                            "stacking": {"group": "A", "mode": "normal"},
                            "thresholdsStyle": {"mode": "off"},
                        },
                        "mappings": [],
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [{"color": "green", "value": None}],
                        },
                        "unit": "short",
                    },
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16},
                "id": 6,
                "options": {
                    "legend": {"calcs": [], "displayMode": "list", "placement": "bottom"},
                    "tooltip": {"mode": "single"},
                },
                "targets": [
                    {
                        "expr": "rate(arkalia_assistantia_prompts_total[5m])",
                        "interval": "",
                        "legendFormat": "Prompts traités/min",
                        "refId": "A",
                    },
                    {
                        "expr": "rate(arkalia_assistantia_security_blocks_total[5m])",
                        "interval": "",
                        "legendFormat": "Blocages sécurité/min",
                        "refId": "B",
                    },
                ],
                "title": "💬 Prompts AssistantIA & Sécurité",
                "type": "timeseries",
            },
            # Panel 7: Erreurs par Module
            {
                "datasource": "prometheus",
                "description": "Erreurs système par module et type",
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "palette-classic"},
                        "custom": {"hideFrom": {"legend": False, "tooltip": False, "vis": False}},
                        "mappings": [],
                        "unit": "short",
                    },
                    "overrides": [],
                },
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16},
                "id": 7,
                "options": {
                    "legend": {"displayMode": "list", "placement": "bottom"},
                    "pieType": "pie",
                    "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
                    "tooltip": {"mode": "single"},
                },
                "targets": [
                    {
                        "expr": "arkalia_errors_total",
                        "interval": "",
                        "legendFormat": "{{module}} - {{error_type}}",
                        "refId": "A",
                    }
                ],
                "title": "🚨 Erreurs par Module",
                "type": "piechart",
            },
        ],
        "refresh": "5s",
        "schemaVersion": 38,
        "style": "dark",
        "tags": ["arkalia", "luna", "monitoring", "overview"],
        "templating": {"list": []},
        "time": {"from": "now-1h", "to": "now"},
        "timepicker": {},
        "timezone": "",
        "title": "🌕 Arkalia-LUNA Pro - Vue d'Ensemble",
        "uid": "arkalia-overview",
        "version": 1,
    }

    return dashboard


def main() -> None:
    """Fonction principale"""
    ark_logger.info(
        "🌕 Génération du Dashboard Grafana Arkalia-LUNA Pro...",
        extra={"arkalia_module": "scripts"},
    )

    # Créer le dashboard
    dashboard = create_arkalia_overview_dashboard()

    # Chemin de sortie
    output_path = Path("infrastructure/monitoring/grafana/dashboards/arkalia_overview.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Sauvegarder le dashboard
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=False)

    ark_logger.info(f"✅ Dashboard créé: {output_path}", extra={"arkalia_module": "scripts"})
    ark_logger.info("📊 Panels inclus:", extra={"arkalia_module": "scripts"})
    ark_logger.info("  • 🕐 Uptime Système", extra={"arkalia_module": "scripts"})
    ark_logger.info("  • 💻 Utilisation CPU/RAM", extra={"arkalia_module": "scripts"})
    ark_logger.info("  • ⚡ Latence & Temps de Réponse", extra={"arkalia_module": "scripts"})
    ark_logger.info("  • 🧠 Décisions ZeroIA/min", extra={"arkalia_module": "scripts"})
    ark_logger.info("  • 🎯 Score de Confiance ZeroIA", extra={"arkalia_module": "scripts"})
    ark_logger.info("  • 💬 Prompts AssistantIA & Sécurité", extra={"arkalia_module": "scripts"})
    ark_logger.info("  • 🚨 Erreurs par Module", extra={"arkalia_module": "scripts"})


if __name__ == "__main__":
    main()
