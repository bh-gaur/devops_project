import os
import logging
import subprocess

logger = logging.getLogger("operator.remediation")

PLAYBOOK_DIR = os.getenv(
    "ANSIBLE_PLAYBOOK_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ansible", "playbooks")),
)

EVENT_PLAYBOOK_MAP = {
    "CrashLoopBackOff": "restart_stuck_service.yaml",
    "OOMKilled": "restart_stuck_service.yaml",
    "DiskPressure": "clean_disk_logs.yaml",
    "NodeDegraded": "drain_degraded_node.yaml",
    "NodeNotReady": "drain_degraded_node.yaml",
    "SecurityViolation": "restart_stuck_service.yaml",
}


def trigger_remediation(event_type: str, payload: dict) -> bool:
    """Dispatches Ansible remediation playbooks based on event classification."""
    playbook_filename = EVENT_PLAYBOOK_MAP.get(event_type)
    if not playbook_filename:
        logger.warning(f"No auto-remediation playbook registered for event type '{event_type}'.")
        return False

    playbook_path = os.path.join(PLAYBOOK_DIR, playbook_filename)
    if not os.path.exists(playbook_path):
        logger.error(f"Playbook file not found at path: {playbook_path}")
        return False

    namespace = payload.get("namespace", "default")
    pod_name = payload.get("pod_name", "")
    node_name = payload.get("node_name", "")
    deployment = payload.get("deployment", "devops-app-rollout")

    extra_vars = f"app_namespace={namespace} pod_name={pod_name} node_name={node_name} deployment={deployment}"


    cmd = [
        "ansible-playbook",
        playbook_path,
        "--extra-vars",
        extra_vars,
    ]

    logger.info(f"Executing auto-remediation playbook '{playbook_filename}' for {event_type}: {extra_vars}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            logger.info(f"Successfully executed remediation for {event_type}.")
            return True
        else:
            logger.error(f"Ansible playbook execution failed: {result.stderr or result.stdout}")
            return False
    except Exception as err:
        logger.error(f"Failed to execute remediation subprocess: {err}")
        return False
