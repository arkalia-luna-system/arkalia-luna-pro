#!/usr/bin/env python3
"""
📊 Script de visualisations avancées pour Arkalia-LUNA Pro
Génère des graphiques et rapports de performance
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.offline as pyo
import seaborn as sns
from plotly.subplots import make_subplots

from core.ark_logger import ark_logger

# Configuration des couleurs Arkalia
ARKALIA_COLORS = {
    "primary": "#1f77b4",  # Bleu principal
    "secondary": "#ff7f0e",  # Orange
    "success": "#2ca02c",  # Vert
    "warning": "#d62728",  # Rouge
    "info": "#9467bd",  # Violet
    "light": "#8c564b",  # Marron
    "dark": "#e377c2",  # Rose
}


class ArkaliaVisualizer:
    """Générateur de visualisations pour Arkalia-LUNA Pro"""

    def __init__(self, output_dir: str = "reports/visualizations") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.colors = ARKALIA_COLORS

        # Configuration matplotlib
        plt.style.use("seaborn-v0_8")
        sns.set_palette(list(self.colors.values()))

    def generate_system_metrics_dashboard(self, days: int = 7) -> None:
        """Génère un dashboard complet des métriques système"""
        ark_logger.info(
            "📊 Génération du dashboard système...", extra={"arkalia_module": "scripts"}
        )

        # Générer des données simulées
        dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]

        # Simuler des métriques système
        np.random.seed(42)
        cpu_usage = (
            50
            + 20 * np.sin(np.linspace(0, 4 * np.pi, len(dates)))
            + np.random.normal(0, 5, len(dates))
        )
        memory_usage = (
            60
            + 15 * np.sin(np.linspace(0, 3 * np.pi, len(dates)))
            + np.random.normal(0, 3, len(dates))
        )
        latency = (
            25
            + 10 * np.sin(np.linspace(0, 5 * np.pi, len(dates)))
            + np.random.normal(0, 2, len(dates))
        )
        errors = np.random.poisson(2, len(dates))

        # Créer le dashboard avec Plotly
        fig = make_subplots(
            rows=3,
            cols=2,
            subplot_titles=(
                "CPU Usage",
                "Memory Usage",
                "Network Latency",
                "Error Rate",
                "System Health",
                "Module Status",
            ),
            specs=[
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
            ],
        )

        # CPU Usage
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=cpu_usage,
                mode="lines",
                name="CPU %",
                line={"color": self.colors["primary"]},
            ),
            row=1,
            col=1,
        )

        # Memory Usage
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=memory_usage,
                mode="lines",
                name="Memory %",
                line={"color": self.colors["secondary"]},
            ),
            row=1,
            col=2,
        )

        # Network Latency
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=latency,
                mode="lines",
                name="Latency (ms)",
                line={"color": self.colors["success"]},
            ),
            row=2,
            col=1,
        )

        # Error Rate
        fig.add_trace(
            go.Bar(
                x=dates,
                y=errors,
                name="Errors",
                marker_color=self.colors["warning"],
            ),
            row=2,
            col=2,
        )

        # System Health (gauge)
        health_score = 85 + np.random.normal(0, 5)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=health_score,
                title={"text": "System Health"},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": self.colors["success"]},
                    "steps": [
                        {"range": [0, 50], "color": "lightgray"},
                        {"range": [50, 80], "color": "yellow"},
                        {"range": [80, 100], "color": "green"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 90,
                    },
                },
            ),
            row=3,
            col=1,
        )

        # Module Status
        modules = ["ReflexIA", "ZeroIA", "Sandozia", "AssistantIA", "Helloria"]
        module_status = [random.choice([0, 1]) for _ in modules]  # nosec B311
        colors = [
            self.colors["success"] if status else self.colors["warning"] for status in module_status
        ]

        fig.add_trace(
            go.Bar(
                x=modules,
                y=module_status,
                name="Module Status",
                marker_color=colors,
            ),
            row=3,
            col=2,
        )

        # Mise à jour du layout
        fig.update_layout(
            title="Arkalia-LUNA Pro - Dashboard Système",
            height=800,
            showlegend=False,
            template="plotly_white",
        )

        # Sauvegarder
        output_path = self.output_dir / "system_dashboard.html"
        pyo.plot(fig, filename=str(output_path), auto_open=False)
        ark_logger.info(
            f"✅ Dashboard sauvegardé: {output_path}", extra={"arkalia_module": "scripts"}
        )

    def generate_performance_timeline(self, hours: int = 24) -> None:
        """Génère une timeline de performance détaillée"""
        ark_logger.info(
            "⏱️ Génération de la timeline de performance...", extra={"arkalia_module": "scripts"}
        )

        # Générer des données horaires
        timestamps = [datetime.now() - timedelta(hours=i) for i in range(hours, 0, -1)]

        # Métriques de performance
        response_times = (
            50
            + 20 * np.sin(np.linspace(0, 6 * np.pi, len(timestamps)))
            + np.random.normal(0, 5, len(timestamps))
        )
        throughput = (
            1000
            + 200 * np.sin(np.linspace(0, 4 * np.pi, len(timestamps)))
            + np.random.normal(0, 50, len(timestamps))
        )
        error_rate = (
            0.5
            + 0.3 * np.sin(np.linspace(0, 8 * np.pi, len(timestamps)))
            + np.random.normal(0, 0.1, len(timestamps))
        )

        # Créer la figure
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle("Arkalia-LUNA Pro - Timeline de Performance", fontsize=16, fontweight="bold")

        # Response Times
        axes[0].plot(timestamps, response_times, color=self.colors["primary"], linewidth=2)
        axes[0].set_title("Temps de Réponse (ms)")
        axes[0].set_ylabel("ms")
        axes[0].grid(True, alpha=0.3)

        # Throughput
        axes[1].plot(timestamps, throughput, color=self.colors["secondary"], linewidth=2)
        axes[1].set_title("Débit (req/s)")
        axes[1].set_ylabel("req/s")
        axes[1].grid(True, alpha=0.3)

        # Error Rate
        axes[2].plot(timestamps, error_rate, color=self.colors["warning"], linewidth=2)
        axes[2].set_title("Taux d'Erreur (%)")
        axes[2].set_ylabel("%")
        axes[2].set_xlabel("Temps")
        axes[2].grid(True, alpha=0.3)

        # Rotation des labels
        for ax in axes:
            ax.tick_params(axis="x", rotation=45)

        plt.tight_layout()

        # Sauvegarder
        output_path = self.output_dir / "performance_timeline.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        ark_logger.info(
            f"✅ Timeline sauvegardée: {output_path}", extra={"arkalia_module": "scripts"}
        )

    def generate_cognitive_load_heatmap(self, days: int = 7) -> None:
        """Génère une heatmap de la charge cognitive"""
        ark_logger.info(
            "🧠 Génération de la heatmap de charge cognitive...",
            extra={"arkalia_module": "scripts"},
        )

        # Données pour la heatmap
        modules = ["ReflexIA", "ZeroIA", "Sandozia", "AssistantIA", "Helloria"]
        hours = list(range(24))

        # Générer des données de charge cognitive
        np.random.seed(42)
        cognitive_load = np.zeros((len(modules), len(hours)))

        for i, _module in enumerate(modules):
            # Charge de base différente par module
            base_load = [0.3, 0.4, 0.6, 0.2, 0.5][i]

            for j, hour in enumerate(hours):
                # Variation circadienne + bruit
                circadian = 0.3 * np.sin(2 * np.pi * (hour - 6) / 24)
                noise = np.random.normal(0, 0.1)
                cognitive_load[i, j] = max(0, min(1, base_load + circadian + noise))

        # Créer la heatmap
        plt.figure(figsize=(15, 8))
        sns.heatmap(
            cognitive_load,
            xticklabels=hours,
            yticklabels=modules,
            cmap="RdYlBu_r",
            annot=True,
            fmt=".2f",
            cbar_kws={"label": "Charge Cognitive"},
        )

        plt.title(
            "Arkalia-LUNA Pro - Charge Cognitive par Module et Heure",
            fontsize=16,
            fontweight="bold",
        )
        plt.xlabel("Heure de la Journée")
        plt.ylabel("Module")

        # Sauvegarder
        output_path = self.output_dir / "cognitive_load_heatmap.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        ark_logger.info(
            f"✅ Heatmap sauvegardée: {output_path}", extra={"arkalia_module": "scripts"}
        )

    def generate_event_timeline(self, events_data: list[dict] | None = None) -> None:
        """Génère une timeline des événements système"""
        ark_logger.info(
            "📅 Génération de la timeline d'événements...", extra={"arkalia_module": "scripts"}
        )

        if events_data is None:
            # Données simulées
            event_types = ["DECISION", "ERROR", "WARNING", "INFO", "SUCCESS"]
            modules = ["ReflexIA", "ZeroIA", "Sandozia", "AssistantIA"]

            events_data = []
            for _i in range(50):
                events_data.append(
                    {
                        "timestamp": datetime.now()
                        - timedelta(hours=random.randint(0, 24)),  # nosec B311
                        "event": random.choice(event_types),  # nosec B311
                        "module": random.choice(modules),  # nosec B311
                        "severity": random.choice(["low", "medium", "high"]),  # nosec B311
                    }
                )

        # Créer la timeline avec Plotly
        fig = go.Figure()

        # Couleurs par type d'événement
        event_colors = {
            "DECISION": self.colors["primary"],
            "ERROR": self.colors["warning"],
            "WARNING": self.colors["secondary"],
            "INFO": self.colors["info"],
            "SUCCESS": self.colors["success"],
        }

        for event in events_data:
            color = event_colors.get(event["event"], self.colors["light"])

            fig.add_trace(
                go.Scatter(
                    x=[event["timestamp"]],
                    y=[event["module"]],
                    mode="markers+text",
                    marker={"size": 15, "color": color},
                    text=event["event"],
                    textposition="top center",
                    name=event["event"],
                    showlegend=False,
                )
            )

        fig.update_layout(
            title="Timeline des Événements Système",
            xaxis_title="Temps",
            yaxis_title="Module",
            height=600,
            template="plotly_white",
        )

        # Sauvegarder
        output_path = self.output_dir / "event_timeline.html"
        pyo.plot(fig, filename=str(output_path), auto_open=False)
        ark_logger.info(
            f"✅ Timeline d'événements sauvegardée: {output_path}",
            extra={"arkalia_module": "scripts"},
        )

    def generate_summary_report(self) -> None:
        """Génère un rapport de synthèse"""
        ark_logger.info(
            "📋 Génération du rapport de synthèse...", extra={"arkalia_module": "scripts"}
        )

        # Statistiques simulées
        stats = {
            "uptime": "99.87%",
            "total_requests": 15420,
            "avg_response_time": "45ms",
            "error_rate": "0.13%",
            "active_modules": 5,
            "system_health": "Excellent",
            "last_maintenance": "2024-01-15",
            "next_maintenance": "2024-02-15",
        }

        # Créer le rapport HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Arkalia-LUNA Pro - Rapport de Synthèse</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: linear-gradient(135deg, {self.colors["primary"]}, 
                          {self.colors["secondary"]});
                          color: white; padding: 20px; border-radius: 10px; }}
                .stats {{ display: grid; 
                         grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                         gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px;
                             border-left: 4px solid {self.colors["primary"]}; }}
                .stat-value {{ font-size: 24px; font-weight: bold; 
                               color: {self.colors["primary"]}; }}
                .stat-label {{ color: #666; margin-top: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌕 Arkalia-LUNA Pro</h1>
                <p>Rapport de Synthèse - {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
            </div>

            <div class="stats">
        """

        for label, value in stats.items():
            html_content += f"""
                <div class="stat-card">
                    <div class="stat-value">{value}</div>
                    <div class="stat-label">{label.replace("_", " ").title()}</div>
                </div>
            """

        html_content += """
            </div>

            <div style="margin-top: 40px;">
                <h2>📊 Visualisations Disponibles</h2>
                <ul>
                    <li><a href="system_dashboard.html">Dashboard Système</a></li>
                    <li><a href="performance_timeline.png">Timeline de Performance</a></li>
                    <li><a href="cognitive_load_heatmap.png">Heatmap de Charge Cognitive</a></li>
                    <li><a href="event_timeline.html">Timeline d'Événements</a></li>
                </ul>
            </div>
        </body>
        </html>
        """

        # Sauvegarder
        output_path = self.output_dir / "summary_report.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        ark_logger.info(
            f"✅ Rapport de synthèse sauvegardé: {output_path}", extra={"arkalia_module": "scripts"}
        )

    def generate_all_visualizations(self) -> None:
        """Génère toutes les visualisations"""
        ark_logger.info(
            "🚀 Génération de toutes les visualisations Arkalia-LUNA Pro...",
            extra={"arkalia_module": "scripts"},
        )

        try:
            self.generate_system_metrics_dashboard()
            self.generate_performance_timeline()
            self.generate_cognitive_load_heatmap()
            self.generate_event_timeline()
            self.generate_summary_report()

            ark_logger.info(
                "🎉 Toutes les visualisations ont été générées avec succès!",
                extra={"arkalia_module": "scripts"},
            )
            ark_logger.info(
                f"📁 Dossier de sortie: {self.output_dir}", extra={"arkalia_module": "scripts"}
            )

        except Exception as e:
            ark_logger.info(
                f"❌ Erreur lors de la génération: {e}", extra={"arkalia_module": "scripts"}
            )


def main():
    """Fonction principale"""
    ark_logger.info(
        "🌕 Arkalia-LUNA Pro - Générateur de Visualisations", extra={"arkalia_module": "scripts"}
    )
    ark_logger.info("=" * 50, extra={"arkalia_module": "scripts"})

    visualizer = ArkaliaVisualizer()
    visualizer.generate_all_visualizations()


if __name__ == "__main__":
    main()
