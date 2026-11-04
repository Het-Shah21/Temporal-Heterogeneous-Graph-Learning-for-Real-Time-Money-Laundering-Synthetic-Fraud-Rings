import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2])
)

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_redpanda_health_uses_transaction_topic_metadata(monkeypatch):
    from backend.app.services import redpanda_service

    class FakeProducer:
        def partitions_for(self, topic):
            assert topic == "transactions"
            return {0}

    monkeypatch.setattr(redpanda_service, "producer", FakeProducer())

    assert redpanda_service.check_redpanda() is True


def test_redpanda_health_returns_false_on_metadata_failure(monkeypatch):
    from backend.app.services import redpanda_service

    class FailingProducer:
        def partitions_for(self, topic):
            raise RuntimeError("metadata unavailable")

    monkeypatch.setattr(redpanda_service, "producer", FailingProducer())

    assert redpanda_service.check_redpanda() is False


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert "services" in data
    assert "redis" in data["services"]
    assert "memgraph" in data["services"]
    assert "redpanda" in data["services"]
