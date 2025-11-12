# 🔥 Test de charge CPU élevée
from tests.chaos.__chaos_common import ChaosTestConfig, ChaosTester


class TestSystemLoadChaos:
    def setup_method(self) -> None:
        self.config = ChaosTestConfig()
        self.chaos = ChaosTester(self.config)

    def teardown_method(self) -> None:
        self.chaos.cleanup()

    def test_system_under_high_cpu_load(self) -> None:
        """Test système sous forte charge CPU"""
        process = self.chaos.simulate_high_load(duration=3)
        assert process is not None
        process.terminate()
