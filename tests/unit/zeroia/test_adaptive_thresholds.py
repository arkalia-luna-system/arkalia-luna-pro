import pytest

from modules.zeroia.adaptive_thresholds import adjust_threshold


@pytest.mark.unit
def test_adjust_threshold_increase() -> None:
    previous = 0.7
    updated = adjust_threshold(current_threshold=previous, feedback="increase")
    assert updated > previous, f"Le seuil aurait dû augmenter mais vaut {updated}"


@pytest.mark.unit
def test_adjust_threshold_decrease() -> None:
    previous = 0.7
    updated = adjust_threshold(current_threshold=previous, feedback="decrease")
    assert updated < previous, f"Le seuil aurait dû diminuer mais vaut {updated}"


@pytest.mark.unit
def test_adjust_threshold_stable() -> None:
    value = 0.5
    updated = adjust_threshold(current_threshold=value, feedback="stable")
    assert updated == value, f"Le seuil devrait rester identique mais vaut {updated}"


@pytest.mark.unit
def test_adjust_threshold_invalid_feedback() -> None:
    value = 0.6
    updated = adjust_threshold(current_threshold=value, feedback="unknown")
    assert (
        updated == value
    ), f"Le seuil devrait rester identique pour feedback invalide mais vaut {updated}"
