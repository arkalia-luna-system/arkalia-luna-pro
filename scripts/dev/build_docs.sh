#!/bin/bash

echo "🔧 [MkDocs] Construction de la documentation"
mkdocs build

echo "📡 [Sitemap] Génération du sitemap"
python3 scripts/sitemap_generator.py
