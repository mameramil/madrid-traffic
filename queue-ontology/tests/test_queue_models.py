"""Basic tests for queue models."""

from queue_ontology.queue_models import mm1_wait_time, mmc_wait_time


def test_mm1_stable():
    result = mm1_wait_time(arrival_rate=10, service_rate=15)
    assert result["utilization"] < 1
    assert result["avg_wait_system_min"] > 0


def test_mm1_unstable():
    result = mm1_wait_time(arrival_rate=20, service_rate=15)
    assert "error" in result


def test_mmc_basic():
    result = mmc_wait_time(arrival_rate=10, service_rate=8, num_servers=2)
    assert result["utilization"] < 1
    assert result["num_servers"] == 2
