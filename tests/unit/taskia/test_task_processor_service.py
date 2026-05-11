import pytest

from modules.taskia.interfaces.formatter_interface import IFormatter
from modules.taskia.services.task_processor import TaskProcessor


class DummyFormatter(IFormatter):
    def get_format_type(self) -> str:
        return "dummy"

    def format(self, data: dict[str, object]) -> str:
        return f"formatted:{data['task']}"


def test_task_processor_processes_valid_context() -> None:
    processor = TaskProcessor(DummyFormatter())

    result = processor.process({"task": "demo"})

    assert result == "formatted:demo"


def test_task_processor_rejects_empty_context() -> None:
    processor = TaskProcessor(DummyFormatter())

    with pytest.raises(ValueError, match="Contexte invalide"):
        processor.process({})

