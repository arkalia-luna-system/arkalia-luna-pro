#!/bin/bash
# 🐳 Arkalia Docker Dev — Rebuild & Run Dev API

echo "🧼 Cleaning containers & volumes..."
docker compose down -v --remove-orphans

echo "🔧 Rebuilding Docker image..."
docker compose build --no-cache

echo "🚀 Starting Arkalia API in dev mode..."
docker compose up -d
