import logging
import sys
from pathlib import Path

import toml

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def check_state_file() -> dict:
    """Check the ZeroIA state file"""
    state_path = Path("modules/zeroia/state/zeroia_state.toml")
    try:
        data = toml.load(state_path)
        logging.info("✅ ZeroIA State file: OK")
        return data
    except Exception as e:
        logging.error(f"💥 ZeroIA State Error: {e}")
        return {}


def check_component_health(state_data: dict) -> bool:
    """Verify component health status"""
    try:
        if not state_data.get("health", {}).get("is_healthy", False):
            logging.error("❌ ZeroIA health check failed")
            return False

        if state_data.get("circuit_breaker", {}).get("state") == "open":
            logging.error("⚡ Circuit breaker is open")
            return False

        if state_data.get("health", {}).get("error_count", 0) > 0:
            logging.warning(f"⚠️ Errors detected: {state_data['health']['error_count']}")

        logging.info("✅ ZeroIA Component health: OK")
        return True
    except Exception as e:
        logging.error(f"💥 Component health check error: {e}")
        return False


def check_performance(state_data: dict) -> bool:
    """Check performance metrics"""
    try:
        perf = state_data.get("performance", {})
        cpu = perf.get("cpu_usage", 0)
        mem = perf.get("memory_usage", 0)

        if cpu > 90 or mem > 90:
            logging.error(f"🔥 Resource usage critical - CPU: {cpu}%, MEM: {mem}%")
            return False

        logging.info(f"📊 Performance - CPU: {cpu}%, MEM: {mem}%")
        return True
    except Exception as e:
        logging.error(f"💥 Performance check error: {e}")
        return False


def main():
    """Main health check routine"""
    try:
        state_data = check_state_file()
        if not state_data:
            sys.exit(1)

        component_healthy = check_component_health(state_data)
        performance_ok = check_performance(state_data)

        if component_healthy and performance_ok:
            logging.info("🎉 All checks passed successfully")
            sys.exit(0)
        else:
            logging.error("❌ One or more checks failed")
            sys.exit(1)
    except Exception as e:
        logging.error(f"💥 Critical error in health check: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
