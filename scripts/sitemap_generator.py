"""Générateur de sitemap pour la documentation MkDocs.

Ce module génère automatiquement un sitemap.xml à partir de la configuration
MkDocs pour améliorer le référencement de la documentation.
"""
import datetime
import os
import urllib.parse

import requests
import yaml

from core.ark_logger import ark_logger


def parse_nav_from_mkdocs(mkdocs_yml_path="mkdocs.yml"):
    """Charge la config MkDocs et extrait les chemins de navigation."""
    with open(mkdocs_yml_path, encoding="utf-8") as f:
        # 🔧 Utilise Loader au lieu de SafeLoader pour supporter les tags Python
        config = yaml.safe_load(f)
    return extract_paths(config.get("nav", []))


def extract_paths(nav, prefix=""):
    """Parcours récursivement la nav pour extraire tous les chemins .md"""
    paths = []

    for item in nav:
        if isinstance(item, dict):
            for _, value in item.items():
                if isinstance(value, list):
                    paths += extract_paths(value, prefix)
                elif isinstance(value, str):
                    path = value.replace(".md", "/").replace("index/", "")
                    paths.append(f"{prefix}{path}")
        elif isinstance(item, str):
            path = item.replace(".md", "/")
            paths.append(f"{prefix}{path}")

    return sorted(set(paths))  # 💡 Supprime les doublons et trie


def generate_sitemap(site_url=None, output_dir="site", mkdocs_yml_path="mkdocs.yml"):
    """Génère un fichier sitemap.xml basé sur la config mkdocs.yml"""
    site_url = site_url or os.getenv(
        "ARKALIA_SITE_URL", "https://arkalia-luna-system.github.io/arkalia-luna-pro"
    )
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    urls = parse_nav_from_mkdocs(mkdocs_yml_path)

    os.makedirs(output_dir, exist_ok=True)
    sitemap_path = os.path.join(output_dir, "sitemap.xml")

    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for path in urls:
            path = path.strip("/")
            full_url = f"{site_url.rstrip('/')}/{path.lstrip('/')}".rstrip("/") + "/"
            f.write("  <url>\n")
            f.write(f"    <loc>{full_url}</loc>\n")
            f.write(f"    <lastmod>{now}</lastmod>\n")
            f.write("  </url>\n")
        f.write("</urlset>\n")

    ark_logger.info(f"✅ Sitemap généré : {sitemap_path}", extra={"arkalia_module": "scripts"})
    ping_google_sitemap()


def generate_sitemap_from_site():
    """Exécution pour script externe (ex: CI/CD)"""
    site_url = "https://arkalia-luna-system.github.io/arkalia-luna-pro"
    generate_sitemap(site_url)


def ping_google_sitemap():
    """Tente de notifier Google de la mise à jour du sitemap."""
    sitemap_url = "https://arkalia-luna-system.github.io/arkalia-luna-pro/sitemap.xml"
    encoded_url = urllib.parse.quote(sitemap_url, safe=":/")
    ping_url = f"https://www.google.com/ping?sitemap={encoded_url}"
    try:
        response = requests.get(ping_url, timeout=5)
        if response.status_code != 200:
            ark_logger.info(
                f"⚠️ Ping échoué ({response.status_code})", extra={"arkalia_module": "scripts"}
            )
    except Exception:
        ark_logger.info("⚠️ Ping désactivé en local.", extra={"arkalia_module": "scripts"})


# 🚀 Exécution directe
if __name__ == "__main__":
    generate_sitemap(
        site_url="https://arkalia-luna-system.github.io/arkalia-luna-pro",
        output_dir="site",
    )
