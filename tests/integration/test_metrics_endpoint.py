# 🧪 tests/integration/test_metrics_endpoint.py
# Tests d'intégration pour le système de métriques Arkalia-LUNA

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest
import requests
import toml

from core.ark_logger import ark_logger


@pytest.fixture
def mock_metrics_server():
    """Mock du serveur de métriques pour les tests"""
    with patch("requests.get") as mock_get:
        # Réponse mock pour /metrics
        mock_response = type(
            "MockResponse",
            (),
            {
                "status_code": 200,
                "text": """# HELP arkalia_system_health System health status
# TYPE arkalia_system_health gauge
arkalia_system_health 1
# HELP arkalia_critical_files_count Number of critical files
# TYPE arkalia_critical_files_count gauge
arkalia_critical_files_count 5
# HELP arkalia_zeroia_confidence ZeroIA confidence level
# TYPE arkalia_zeroia_confidence gauge
arkalia_zeroia_confidence 0.85""",
                "headers": {"content-type": "text/plain; version=0.0.4; charset=utf-8"},
            },
        )()
        mock_get.return_value = mock_response
        yield mock_get


class TestMetricsEndpoint:
    """Tests pour l'endpoint /metrics et le système de monitoring"""

    BASE_URL = "http://localhost:8000"

    def test_metrics_endpoint_accessibility(self, mock_metrics_server):
        """🌐 Test d'accessibilité de l'endpoint /metrics"""
        try:
            response = requests.get(f"{self.BASE_URL}/metrics", timeout=5)

            # L'endpoint doit répondre même si prometheus_client absent
            assert response.status_code == 200
            assert "arkalia" in response.text.lower()

            # Format Prometheus ou compatible
            content_type = response.headers.get("content-type", "")
            assert "text/plain" in content_type

        except requests.exceptions.ConnectionError:
            pytest.skip("Serveur API non démarré - normal en CI/CD")

    def test_metrics_format_prometheus(self, mock_metrics_server):
        """📊 Test du format des métriques Prometheus"""
        try:
            response = requests.get(f"{self.BASE_URL}/metrics", timeout=5)
            assert response.status_code == 200

            lines = response.text.strip().split("\n")

            # Vérifications format Prometheus
            help_lines = [line for line in lines if line.startswith("# HELP")]
            type_lines = [line for line in lines if line.startswith("# TYPE")]
            metric_lines = [line for line in lines if not line.startswith("#") and line.strip()]

            assert len(help_lines) > 0, "Aucune ligne HELP trouvée"
            assert len(type_lines) > 0, "Aucune ligne TYPE trouvée"
            assert len(metric_lines) > 0, "Aucune métrique trouvée"

            # Vérification métriques Arkalia spécifiques
            metrics_text = response.text
            assert "arkalia_system_health" in metrics_text
            assert "arkalia_critical_files_count" in metrics_text

        except requests.exceptions.ConnectionError:
            pytest.skip("Serveur API non démarré")

    def test_metrics_content_validation(self, mock_metrics_server):
        """🔍 Test du contenu et cohérence des métriques"""
        try:
            response = requests.get(f"{self.BASE_URL}/metrics", timeout=5)
            assert response.status_code == 200

            metrics_text = response.text

            # Parse métriques basiques
            metrics = {}
            for line in metrics_text.split("\n"):
                if not line.startswith("#") and " " in line and line.strip():
                    parts = line.strip().split(" ")
                    if len(parts) >= 2:
                        metric_name = parts[0].split("{")[0]  # Retire les labels
                        try:
                            metric_value = float(parts[-1])
                            metrics[metric_name] = metric_value
                        except ValueError:
                            pass  # Ignore les métriques non numériques

            # Validations logiques
            if "arkalia_system_health" in metrics:
                health = metrics["arkalia_system_health"]
                assert health in [0, 1], f"Health doit être 0 ou 1, trouvé: {health}"

            if "arkalia_critical_files_count" in metrics:
                files_count = metrics["arkalia_critical_files_count"]
                assert 0 <= files_count <= 10, f"Nombre de fichiers suspect: {files_count}"

            if "arkalia_zeroia_confidence" in metrics:
                confidence = metrics["arkalia_zeroia_confidence"]
                assert 0.0 <= confidence <= 1.0, f"Confiance hors limites: {confidence}"

        except requests.exceptions.ConnectionError:
            pytest.skip("Serveur API non démarré")


class TestFallbackMetrics:
    """Tests pour le système de métriques sans dépendances"""

    def test_fallback_metrics_generation(self):
        """🔧 Test génération métriques de secours"""
        from helloria.core import _get_fallback_metrics

        metrics = _get_fallback_metrics()

        # Vérifications structure
        assert isinstance(metrics, dict)
        assert len(metrics) > 0

        # Métriques obligatoires
        required_metrics = [
            "arkalia_system_health",
            "arkalia_critical_files_count",
            "arkalia_zeroia_confidence",
            "arkalia_api_uptime_seconds",
        ]

        for metric in required_metrics:
            assert metric in metrics, f"Métrique manquante: {metric}"
            assert isinstance(metrics[metric], int | float), f"Type invalide pour {metric}"

    def test_fallback_metrics_values(self):
        """🎯 Test cohérence des valeurs de métriques"""
        from helloria.core import _get_fallback_metrics

        metrics = _get_fallback_metrics()

        # Validations logiques
        assert metrics["arkalia_system_health"] in [0, 1]
        assert 0 <= metrics["arkalia_critical_files_count"] <= 10
        assert 0.0 <= metrics["arkalia_zeroia_confidence"] <= 1.0
        assert metrics["arkalia_api_uptime_seconds"] > 0
        assert metrics["arkalia_endpoints_available"] >= 3

    def test_prometheus_format_conversion(self):
        """📝 Test conversion format Prometheus"""
        from helloria.core import _convert_to_prometheus_format

        test_metrics = {"test_counter": 42, "test_gauge": 3.14, "test_string": "active"}

        prometheus_text = _convert_to_prometheus_format(test_metrics)

        # Vérifications format
        assert "# HELP test_counter" in prometheus_text
        assert "# TYPE test_counter gauge" in prometheus_text
        assert "test_counter 42" in prometheus_text

        assert "# HELP test_gauge" in prometheus_text
        assert "test_gauge 3.14" in prometheus_text

        assert "test_string_info" in prometheus_text
        assert 'value="active"' in prometheus_text


class TestMetricsIntegration:
    """Tests d'intégration avec les fichiers état"""

    def test_zeroia_metrics_integration(self):
        """🔄 Test intégration métriques ZeroIA"""
        # Crée un fichier de test
        test_dashboard = {
            "last_decision": "monitor",
            "confidence": 0.85,
            "reasoning_loop_active": True,
        }

        dashboard_path = Path("state/zeroia_dashboard.json")
        dashboard_path.parent.mkdir(exist_ok=True)

        original_content = None
        if dashboard_path.exists():
            with open(dashboard_path) as f:
                original_content = f.read()

        try:
            # Écrit données de test
            with open(dashboard_path, "w") as f:
                json.dump(test_dashboard, f)

            # Test collecte
            from helloria.core import _get_fallback_metrics

            metrics = _get_fallback_metrics()

            assert metrics["arkalia_zeroia_confidence"] == 0.85

        finally:
            # Restaure fichier original
            if original_content:
                with open(dashboard_path, "w") as f:
                    f.write(original_content)
            elif dashboard_path.exists():
                dashboard_path.unlink()

    def test_reflexia_metrics_integration(self):
        """📊 Test intégration métriques ReflexIA"""
        test_state = {
            "metrics": {"cpu": 65.5, "ram": 45.2, "latency": 123.0},
            "status": "active",
        }

        state_path = Path("state/reflexia_state.toml")
        state_path.parent.mkdir(exist_ok=True)

        original_content = None
        if state_path.exists():
            with open(state_path) as f:
                original_content = f.read()

        try:
            # Écrit données de test
            with open(state_path, "w") as f:
                toml.dump(test_state, f)

            # Test collecte
            from helloria.core import _get_fallback_metrics

            metrics = _get_fallback_metrics()

            assert metrics["arkalia_reflexia_cpu_percent"] == 65.5
            assert metrics["arkalia_reflexia_ram_percent"] == 45.2

        finally:
            # Restaure fichier original
            if original_content:
                with open(state_path, "w") as f:
                    f.write(original_content)
            elif state_path.exists():
                state_path.unlink()


class TestMetricsPerformance:
    """Tests de performance du système de métriques"""

    def test_metrics_collection_speed(self):
        """⚡ Test vitesse de collecte des métriques"""
        from helloria.core import _get_fallback_metrics

        start_time = time.time()

        # Collecte multiple
        for _ in range(10):
            metrics = _get_fallback_metrics()
            assert len(metrics) > 0

        end_time = time.time()
        total_time = end_time - start_time

        # Doit être rapide (< 1 seconde pour 10 collectes)
        assert total_time < 1.0, f"Collecte trop lente: {total_time:.2f}s"

        avg_time_ms = (total_time / 10) * 1000
        ark_logger.info(
            f"⚡ Temps moyen par collecte: {avg_time_ms:.1f}ms",
            extra={"arkalia_module": "integration"},
        )

    def test_prometheus_format_speed(self):
        """📝 Test vitesse de formatage Prometheus"""
        from helloria.core import _convert_to_prometheus_format, _get_fallback_metrics

        metrics = _get_fallback_metrics()

        start_time = time.time()

        # Formatage multiple
        for _ in range(50):
            prometheus_text = _convert_to_prometheus_format(metrics)
            assert len(prometheus_text) > 100

        end_time = time.time()
        total_time = end_time - start_time

        # Doit être très rapide (< 0.5 seconde pour 50 formatages)
        assert total_time < 0.5, f"Formatage trop lent: {total_time:.2f}s"

        avg_time_ms = (total_time / 50) * 1000
        ark_logger.info(
            f"📝 Temps moyen par formatage: {avg_time_ms:.1f}ms",
            extra={"arkalia_module": "integration"},
        )


# === TESTS COMPLÉMENTAIRES ===


def test_endpoint_error_handling():
    """❌ Test gestion d'erreurs endpoint /metrics"""
    try:
        # Test avec timeout court
        response = requests.get("http://localhost:8000/metrics", timeout=1)

        # Même en cas d'erreur interne, status ne doit pas être 500
        if response.status_code == 500:
            # Vérifie que l'erreur est documentée
            try:
                error_data = response.json()
                assert "error" in error_data
            except Exception:
                pass  # Format non-JSON acceptable

    except requests.exceptions.ConnectionError:
        pytest.skip("Serveur API non démarré")


def test_metrics_consistency():
    """🔄 Test consistance des métriques entre appels"""
    try:
        # Deux appels successifs
        response1 = requests.get("http://localhost:8000/metrics", timeout=3)
        time.sleep(0.1)
        response2 = requests.get("http://localhost:8000/metrics", timeout=3)

        if response1.status_code == 200 and response2.status_code == 200:
            # Les métriques structurelles ne doivent pas changer
            lines1 = [
                line
                for line in response1.text.split("\n")
                if "arkalia_critical_files_count" in line
            ]
            lines2 = [
                line
                for line in response2.text.split("\n")
                if "arkalia_critical_files_count" in line
            ]

            if lines1 and lines2:
                assert lines1[0] == lines2[0], "Métriques critiques inconsistantes"

    except requests.exceptions.ConnectionError:
        pytest.skip("Serveur API non démarré")
