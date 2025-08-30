#!/usr/bin/env python3
"""
🔍 Script de validation complète du monitoring Arkalia-LUNA Pro
Vérifie tous les composants de monitoring et génère un rapport détaillé
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any

import aiohttp
import psutil

from core.ark_logger import ark_logger

# Configuration logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MonitoringValidator:
    """Validateur complet du monitoring Arkalia"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "components": {},
            "metrics": {},
            "alerts": {},
            "recommendations": [],
        }

        # URLs des services
        self.services = {
            "arkalia_api": "http://localhost:8000",
            "prometheus": "http://localhost:9090",
            "grafana": "http://localhost:3000",
            "alertmanager": "http://localhost:9093",
            "loki": "http://localhost:3100",
            "node_exporter": "http://localhost:9100",
            "cadvisor": "http://localhost:8080",
        }

        # Credentials Grafana
        self.grafana_auth = aiohttp.BasicAuth("admin", "arkalia-secure-2025")

    async def check_service_health(
        self, session: aiohttp.ClientSession, name: str, url: str
    ) -> dict[str, Any]:
        """Vérifie la santé d'un service"""
        try:
            start_time = time.time()
            health_url = f"{url}/health" if name != "arkalia_api" else f"{url}/health"
            async with session.get(health_url, timeout=5) as response:
                duration = time.time() - start_time
                return {
                    "status": "healthy" if response.status == 200 else "unhealthy",
                    "response_time": round(duration, 3),
                    "status_code": response.status,
                    "error": None,
                }
        except Exception as e:
            return {"status": "error", "response_time": None, "status_code": None, "error": str(e)}

    async def check_arkalia_metrics(self, session: aiohttp.ClientSession) -> dict[str, Any]:
        """Vérifie les métriques Arkalia"""
        try:
            async with session.get(
                f"{self.services['arkalia_api']}/metrics", timeout=10
            ) as response:
                if response.status == 200:
                    metrics_text = await response.text()
                    arkalia_metrics = [
                        line for line in metrics_text.split("\n") if line.startswith("arkalia_")
                    ]

                    return {
                        "status": "healthy",
                        "total_metrics": len(arkalia_metrics),
                        "sample_metrics": arkalia_metrics[:5],
                        "error": None,
                    }
                else:
                    return {
                        "status": "error",
                        "total_metrics": 0,
                        "sample_metrics": [],
                        "error": f"HTTP {response.status}",
                    }
        except Exception as e:
            return {"status": "error", "total_metrics": 0, "sample_metrics": [], "error": str(e)}

    async def check_prometheus_targets(self, session: aiohttp.ClientSession) -> dict[str, Any]:
        """Vérifie les targets Prometheus"""
        try:
            async with session.get(
                f"{self.services['prometheus']}/api/v1/targets", timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    targets = data.get("data", {}).get("activeTargets", [])
                    arkalia_targets = [
                        t for t in targets if "arkalia" in t.get("labels", {}).get("job", "")
                    ]

                    return {
                        "status": "healthy",
                        "total_targets": len(targets),
                        "arkalia_targets": len(arkalia_targets),
                        "targets_status": {
                            t["labels"]["job"]: t["health"] for t in arkalia_targets
                        },
                        "error": None,
                    }
                else:
                    return {
                        "status": "error",
                        "total_targets": 0,
                        "arkalia_targets": 0,
                        "targets_status": {},
                        "error": f"HTTP {response.status}",
                    }
        except Exception as e:
            return {
                "status": "error",
                "total_targets": 0,
                "arkalia_targets": 0,
                "targets_status": {},
                "error": str(e),
            }

    async def check_grafana_dashboards(self, session: aiohttp.ClientSession) -> dict[str, Any]:
        """Vérifie les dashboards Grafana"""
        try:
            async with session.get(
                f"{self.services['grafana']}/api/search", auth=self.grafana_auth, timeout=10
            ) as response:
                if response.status == 200:
                    dashboards = await response.json()
                    arkalia_dashboards = [
                        d for d in dashboards if "arkalia" in d.get("title", "").lower()
                    ]

                    return {
                        "status": "healthy",
                        "total_dashboards": len(dashboards),
                        "arkalia_dashboards": len(arkalia_dashboards),
                        "dashboard_titles": [d["title"] for d in arkalia_dashboards],
                        "error": None,
                    }
                else:
                    return {
                        "status": "error",
                        "total_dashboards": 0,
                        "arkalia_dashboards": 0,
                        "dashboard_titles": [],
                        "error": f"HTTP {response.status}",
                    }
        except Exception as e:
            return {
                "status": "error",
                "total_dashboards": 0,
                "arkalia_dashboards": 0,
                "dashboard_titles": [],
                "error": str(e),
            }

    def check_system_resources(self) -> dict[str, Any]:
        """Vérifie les ressources système"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "status": "healthy",
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "error": None,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def generate_recommendations(self) -> list[str]:
        """Génère des recommandations basées sur les résultats"""
        recommendations = []

        # Vérifier les services
        for service_name, service_data in self.results["components"].items():
            if service_data.get("status") != "healthy":
                recommendations.append(
                    f"🔧 Corriger le service {service_name}: {service_data.get('error', 'Unknown error')}"
                )

        # Vérifier les métriques
        metrics_data = self.results.get("metrics", {})
        if metrics_data.get("arkalia_metrics", {}).get("total_metrics", 0) < 10:
            recommendations.append("📊 Augmenter le nombre de métriques Arkalia exposées")

        # Vérifier les dashboards
        grafana_data = self.results.get("components", {}).get("grafana_dashboards", {})
        if grafana_data.get("arkalia_dashboards", 0) == 0:
            recommendations.append("📈 Créer des dashboards Arkalia dans Grafana")

        # Vérifier les ressources système
        system_data = self.results.get("components", {}).get("system_resources", {})
        if system_data.get("status") == "healthy":
            cpu = system_data.get("cpu_percent", 0)
            memory = system_data.get("memory_percent", 0)
            disk = system_data.get("disk_percent", 0)

            if cpu > 80:
                recommendations.append("⚡ CPU élevé - Optimiser les performances")
            if memory > 80:
                recommendations.append("💾 Mémoire élevée - Vérifier les fuites mémoire")
            if disk > 90:
                recommendations.append("💿 Espace disque critique - Nettoyer les logs")

        if not recommendations:
            recommendations.append("✅ Tous les composants sont optimaux")

        return recommendations

    async def run_validation(self) -> dict[str, Any]:
        """Exécute la validation complète"""
        logger.info("🔍 Démarrage de la validation du monitoring Arkalia...")

        async with aiohttp.ClientSession() as session:
            # Vérifier la santé des services
            logger.info("📡 Vérification de la santé des services...")
            for service_name, service_url in self.services.items():
                self.results["components"][service_name] = await self.check_service_health(
                    session, service_name, service_url
                )

            # Vérifier les métriques Arkalia
            logger.info("📊 Vérification des métriques Arkalia...")
            self.results["metrics"]["arkalia_metrics"] = await self.check_arkalia_metrics(session)

            # Vérifier les targets Prometheus
            logger.info("🎯 Vérification des targets Prometheus...")
            self.results["components"]["prometheus_targets"] = await self.check_prometheus_targets(
                session
            )

            # Vérifier les dashboards Grafana
            logger.info("📈 Vérification des dashboards Grafana...")
            self.results["components"]["grafana_dashboards"] = await self.check_grafana_dashboards(
                session
            )

            # Vérifier les ressources système
            logger.info("💻 Vérification des ressources système...")
            self.results["components"]["system_resources"] = self.check_system_resources()

        # Générer les recommandations
        self.results["recommendations"] = self.generate_recommendations()

        # Déterminer le statut global
        healthy_services = sum(
            1
            for service in self.results["components"].values()
            if service.get("status") == "healthy"
        )
        total_services = len(self.results["components"])

        if healthy_services == total_services:
            self.results["overall_status"] = "excellent"
        elif healthy_services >= total_services * 0.8:
            self.results["overall_status"] = "good"
        elif healthy_services >= total_services * 0.6:
            self.results["overall_status"] = "warning"
        else:
            self.results["overall_status"] = "critical"

        logger.info(f"✅ Validation terminée - Statut: {self.results['overall_status']}")
        return self.results

    def print_report(self):
        """Affiche le rapport de validation"""
        ark_logger.info("\n" + "=" * 80, extra={"arkalia_module": "scripts"})
        ark_logger.info(
            "🔍 RAPPORT DE VALIDATION DU MONITORING ARKALIA-LUNA PRO",
            extra={"arkalia_module": "scripts"},
        )
        ark_logger.info("=" * 80, extra={"arkalia_module": "scripts"})
        ark_logger.info(
            f"📅 Timestamp: {self.results['timestamp']}", extra={"arkalia_module": "scripts"}
        )
        ark_logger.info(
            f"🎯 Statut global: {self.results['overall_status'].upper()}",
            extra={"arkalia_module": "scripts"},
        )

        ark_logger.info("\n📡 SERVICES:", extra={"arkalia_module": "scripts"})
        for service_name, service_data in self.results["components"].items():
            status_emoji = "✅" if service_data.get("status") == "healthy" else "❌"
            ark_logger.info(
                f"  {status_emoji} {service_name}: {service_data.get('status', 'unknown')}",
                extra={"arkalia_module": "scripts"},
            )
            if service_data.get("error"):
                ark_logger.error(
                    f"     Erreur: {service_data['error']}", extra={"arkalia_module": "scripts"}
                )

        ark_logger.info("\n📊 MÉTRIQUES:", extra={"arkalia_module": "scripts"})
        metrics_data = self.results.get("metrics", {}).get("arkalia_metrics", {})
        ark_logger.info(
            f"  📈 Métriques Arkalia: {metrics_data.get('total_metrics', 0)}",
            extra={"arkalia_module": "scripts"},
        )
        if metrics_data.get("sample_metrics"):
            ark_logger.info(
                f"     Exemples: {', '.join(metrics_data['sample_metrics'][:3])}",
                extra={"arkalia_module": "scripts"},
            )

        ark_logger.info("\n💻 RESSOURCES SYSTÈME:", extra={"arkalia_module": "scripts"})
        system_data = self.results.get("components", {}).get("system_resources", {})
        if system_data.get("status") == "healthy":
            ark_logger.info(
                f"  🖥️  CPU: {system_data.get('cpu_percent', 0)}%",
                extra={"arkalia_module": "scripts"},
            )
            ark_logger.info(
                f"  💾 RAM: {system_data.get('memory_percent', 0)}% ({system_data.get('memory_used_gb', 0)}GB/{system_data.get('memory_total_gb', 0)}GB)",
                extra={"arkalia_module": "scripts"},
            )
            ark_logger.info(
                f"  💿 Disque: {system_data.get('disk_percent', 0)}% ({system_data.get('disk_used_gb', 0)}GB/{system_data.get('disk_total_gb', 0)}GB)",
                extra={"arkalia_module": "scripts"},
            )

        ark_logger.info("\n💡 RECOMMANDATIONS:", extra={"arkalia_module": "scripts"})
        for rec in self.results["recommendations"]:
            ark_logger.info(f"  {rec}", extra={"arkalia_module": "scripts"})

        ark_logger.info("\n" + "=" * 80, extra={"arkalia_module": "scripts"})
        ark_logger.info("🌐 URLs d'accès:", extra={"arkalia_module": "scripts"})
        ark_logger.info(
            "  📊 Grafana: http://localhost:3000 (admin/arkalia-secure-2025)",
            extra={"arkalia_module": "scripts"},
        )
        ark_logger.info(
            "  🎯 Prometheus: http://localhost:9090", extra={"arkalia_module": "scripts"}
        )
        ark_logger.info(
            "  🚨 AlertManager: http://localhost:9093", extra={"arkalia_module": "scripts"}
        )
        ark_logger.info("  📝 Loki: http://localhost:3100", extra={"arkalia_module": "scripts"})
        ark_logger.info("  🔧 cAdvisor: http://localhost:8080", extra={"arkalia_module": "scripts"})
        ark_logger.info("=" * 80, extra={"arkalia_module": "scripts"})


async def main():
    """Fonction principale"""
    validator = MonitoringValidator()
    results = await validator.run_validation()
    validator.print_report()

    # Sauvegarder le rapport
    import os

    os.makedirs("logs", exist_ok=True)
    report_file = f"logs/monitoring_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    ark_logger.info(f"\n📄 Rapport sauvegardé: {report_file}", extra={"arkalia_module": "scripts"})

    return results


if __name__ == "__main__":
    asyncio.run(main())
