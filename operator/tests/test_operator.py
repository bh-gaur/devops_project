import pytest
from watcher import parse_k8s_event
from remediation_engine import EVENT_PLAYBOOK_MAP, trigger_remediation


def test_parse_k8s_event_crashloop():
    event_data = {
        "reason": "BackOff",
        "message": "Back-off restarting failed container in pod devops-app-123 (CrashLoopBackOff)",
        "involvedObject": {
            "kind": "Pod",
            "name": "devops-app-123",
            "namespace": "default",
        },
    }
    event_type, payload = parse_k8s_event(event_data)
    assert event_type == "CrashLoopBackOff"
    assert payload["pod_name"] == "devops-app-123"
    assert payload["namespace"] == "default"


def test_parse_k8s_event_diskpressure():
    event_data = {
        "reason": "DiskPressure",
        "message": "Node has disk pressure",
        "involvedObject": {
            "kind": "Node",
            "name": "worker-node-1",
            "namespace": "default",
        },
    }
    event_type, payload = parse_k8s_event(event_data)
    assert event_type == "DiskPressure"
    assert payload["node_name"] == "worker-node-1"


def test_event_playbook_mapping():
    assert EVENT_PLAYBOOK_MAP["CrashLoopBackOff"] == "restart_stuck_service.yaml"
    assert EVENT_PLAYBOOK_MAP["OOMKilled"] == "restart_stuck_service.yaml"
    assert EVENT_PLAYBOOK_MAP["DiskPressure"] == "clean_disk_logs.yaml"
    assert EVENT_PLAYBOOK_MAP["NodeDegraded"] == "drain_degraded_node.yaml"


def test_trigger_remediation_unregistered():
    result = trigger_remediation("UnknownEvent", {})
    assert result is False
