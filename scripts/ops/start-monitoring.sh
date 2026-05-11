#!/bin/bash
# 📊 scripts/ops/start-monitoring.sh
# Démarrage et test du stack monitoring Arkalia-LUNA Phase 4

set -euo pipefail

# Configuration
MONITORING_DIR="infrastructure/monitoring"
COMPOSE_FILE="$MONITORING_DIR/docker-compose.monitoring.yml"
PROMETHEUS_URL="http://localhost:9090"
GRAFANA_URL="http://localhost:3000"
ALERTMANAGER_URL="http://localhost:9093"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Header
echo -e "${BLUE}"
cat << 'EOF'
📊 =======================================
   ARKALIA-LUNA MONITORING STACK
   Phase 4 Security Operations Center
========================================
EOF
echo -e "${NC}"

log "🚀 Starting Arkalia-LUNA monitoring infrastructure..."

# Vérification Docker
if ! command -v docker &> /dev/null; then
    error "Docker not found - required for monitoring stack"
fi

if ! command -v docker compose &> /dev/null; then
    error "Docker Compose not found - required for monitoring stack"
fi

# Vérification fichiers de configuration
log "📋 Checking configuration files..."

required_configs=(
    "$MONITORING_DIR/prometheus/prometheus.yml"
    "$MONITORING_DIR/prometheus/alerting_rules.yml"
    "$MONITORING_DIR/alertmanager/config.yml"
    "$MONITORING_DIR/loki/config.yml"
    "$MONITORING_DIR/grafana/dashboards/security-ops.json"
)

for config in "${required_configs[@]}"; do
    if [[ -f "$config" ]]; then
        success "✅ $config"
    else
        error "❌ Missing config: $config"
    fi
done

# Création des volumes et répertoires
log "📁 Setting up volumes and directories..."
mkdir -p "$MONITORING_DIR/promtail"
mkdir -p "$MONITORING_DIR/grafana/datasources"

# Configuration Promtail pour les logs Arkalia
cat > "$MONITORING_DIR/promtail/config.yml" << 'EOF'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: arkalia-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: arkalia-system
          __path__: /arkalia/logs/*.log

  - job_name: zeroia-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: zeroia
          component: cognitive
          __path__: /arkalia/logs/zeroia*.log

  - job_name: security-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: security
          component: phase4
          __path__: /arkalia/logs/*security*.log
EOF

# Configuration Grafana datasources
cat > "$MONITORING_DIR/grafana/datasources/datasources.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: true

  - name: AlertManager
    type: alertmanager
    access: proxy
    url: http://alertmanager:9093
    editable: true
EOF

# Arrêt éventuel de l'ancien stack
log "🛑 Stopping any existing monitoring stack..."
docker compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true

# Démarrage du nouveau stack
log "🚀 Starting monitoring stack..."
docker compose -f "$COMPOSE_FILE" up -d

# Attente démarrage services
log "⏳ Waiting for services to start..."
sleep 15

# Tests de santé
log "🩺 Running health checks..."

# Test Prometheus
if curl -s "$PROMETHEUS_URL/api/v1/status/config" > /dev/null; then
    success "✅ Prometheus is healthy"
else
    warning "⚠️ Prometheus not responding"
fi

# Test Grafana
if curl -s "$GRAFANA_URL/api/health" > /dev/null; then
    success "✅ Grafana is healthy"
else
    warning "⚠️ Grafana not responding"
fi

# Test AlertManager
if curl -s "$ALERTMANAGER_URL/api/v1/status" > /dev/null; then
    success "✅ AlertManager is healthy"
else
    warning "⚠️ AlertManager not responding"
fi

# Test Loki
if curl -s "http://localhost:3100/ready" > /dev/null; then
    success "✅ Loki is healthy"
else
    warning "⚠️ Loki not responding"
fi

# Affichage des logs en temps réel
log "📊 Monitoring stack status:"
docker compose -f "$COMPOSE_FILE" ps

# Informations d'accès
echo -e "\n${GREEN}🎯 MONITORING ENDPOINTS${NC}"
echo "=================================="
echo "📊 Prometheus:    $PROMETHEUS_URL"
echo "📈 Grafana:       $GRAFANA_URL (admin/arkalia-secure-2025)"
echo "🚨 AlertManager:  $ALERTMANAGER_URL"
echo "📋 Loki:         http://localhost:3100"
echo "🖥️  Node Exporter: http://localhost:9100"
echo "🐳 cAdvisor:      http://localhost:8080"

echo -e "\n${BLUE}📚 QUICK START GUIDE${NC}"
echo "=================================="
echo "1. 📊 Open Grafana: $GRAFANA_URL"
echo "2. 🔑 Login: admin / arkalia-secure-2025"
echo "3. 📈 Import Security Operations Center dashboard"
echo "4. 🚨 Check AlertManager for active alerts"
echo "5. 📋 Browse logs in Loki datasource"

echo -e "\n${YELLOW}🔧 MANAGEMENT COMMANDS${NC}"
echo "=================================="
echo "📊 View logs:       docker compose -f $COMPOSE_FILE logs -f"
echo "🛑 Stop stack:      docker compose -f $COMPOSE_FILE down"
echo "🔄 Restart stack:   docker compose -f $COMPOSE_FILE restart"
echo "📈 Scale Grafana:   docker compose -f $COMPOSE_FILE up -d --scale grafana=2"

# Test final d'intégration
log "🧪 Running integration tests..."

# Test ingestion métriques
if curl -s "$PROMETHEUS_URL/api/v1/query?query=up" | grep -q "success"; then
    success "✅ Prometheus metrics ingestion working"
else
    warning "⚠️ Metrics ingestion issues detected"
fi

# Test des alerting rules
if curl -s "$PROMETHEUS_URL/api/v1/rules" | grep -q "arkalia"; then
    success "✅ Arkalia alerting rules loaded"
else
    warning "⚠️ Alerting rules not loaded"
fi

log "🎉 Monitoring stack deployment completed!"
echo -e "\n${GREEN}💣 ARKALIA-LUNA PHASE 4 MONITORING: ACTIVE! 📊${NC}"
