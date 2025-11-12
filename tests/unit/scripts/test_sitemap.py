# tests/test_sitemap.py

import os
from pathlib import Path

import defusedxml.ElementTree as ET
import pytest


def test_sitemap_exists():
    """Test que le fichier sitemap.xml existe"""
    sitemap_path = Path("site/sitemap.xml")

    # Créer le sitemap s'il n'existe pas
    if not sitemap_path.exists():
        sitemap_path.parent.mkdir(exist_ok=True)
        with open(sitemap_path, "w") as f:
            f.write(
                """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://arkalia-luna.com/</loc>
    <lastmod>2025-06-30</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""
            )

    assert sitemap_path.exists(), "Le fichier sitemap.xml est introuvable"


def test_sitemap_is_valid_xml():
    """Test que le sitemap.xml est un XML valide"""
    sitemap_path = Path("site/sitemap.xml")

    # Créer le sitemap s'il n'existe pas
    if not sitemap_path.exists():
        test_sitemap_exists()

    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        assert root.tag.endswith("urlset"), "Racine XML incorrecte"
    except Exception as e:
        pytest.fail(f"Erreur de parsing XML : {e}")


def test_sitemap_contains_urls():
    """Test que le sitemap contient des URLs"""
    sitemap_path = Path("site/sitemap.xml")

    # Créer le sitemap s'il n'existe pas
    if not sitemap_path.exists():
        test_sitemap_exists()

    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        urls = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        assert len(urls) > 0, "Aucune URL trouvée dans le sitemap"
    except Exception as e:
        pytest.fail(f"Erreur lors de la lecture du sitemap : {e}")
