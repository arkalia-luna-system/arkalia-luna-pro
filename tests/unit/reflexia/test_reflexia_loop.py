from modules.reflexia.logic.main_loop_enhanced import reflexia_loop


def test_reflexia_loop_limited() -> None:
    # Exécute seulement 2 itérations
    reflexia_loop(max_iterations=2, sleep_seconds=0.1)
