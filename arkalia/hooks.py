from typing import Any

from core.ark_logger import ark_logger
from scripts.sitemap_generator import generate_sitemap_from_site


def generate_sitemap(config: dict[str, Any] | None = None, **kwargs: Any) -> None:
    """
    Hook pour générer le sitemap.xml après la construction du site.
    """
    generate_sitemap_from_site()


def before_startup() -> None:
    """
    Fonction à exécuter avant le démarrage de l'application.
    Utilisée pour initialiser ou vérifier certains éléments.
    """
    ark_logger.info("Initialisation avant le démarrage", extra={"arkalia_module": "arkalia"})
    # Placeholder désactivé pour éviter erreurs F821
    # Exemple : initialiser base de données, logs, etc.
    return None
