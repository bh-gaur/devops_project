import os
import time
import logging
try:
    from operator.remediation_engine import trigger_remediation
except (ImportError, ModuleNotFoundError):
    from remediation_engine import trigger_remediation


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("operator.watcher")


def parse_k8s_event(event_data: dict) -> tuple[str, dict]:
    """Extracts event classification and payload details from a K8s event dictionary."""
    reason = event_data.get("reason", "")
    message = event_data.get("message", "")
    object_meta = event_data.get("involvedObject", {})

    event_type = ""
    if "CrashLoopBackOff" in reason or "CrashLoopBackOff" in message:
        event_type = "CrashLoopBackOff"
    elif "OOMKilled" in reason or "OOMKilled" in message:
        event_type = "OOMKilled"
    elif "DiskPressure" in reason or "DiskPressure" in message:
        event_type = "DiskPressure"
    elif "NodeNotReady" in reason or "NodeNotReady" in message:
        event_type = "NodeNotReady"

    payload = {
        "namespace": object_meta.get("namespace", "default"),
        "pod_name": object_meta.get("name", "") if object_meta.get("kind") == "Pod" else "",
        "node_name": object_meta.get("name", "") if object_meta.get("kind") == "Node" else "",
        "reason": reason,
        "message": message,
    }

    return event_type, payload


def start_k8s_watcher():
    """Starts Python Kubernetes Event Watcher daemon."""
    logger.info("Initializing Autonomous Kubernetes Event Watcher daemon...")
    try:
        from kubernetes import client, config, watch
        
        try:
            config.load_incluster_config()
        except Exception:
            config.load_kube_config()

        v1 = client.CoreV1Api()
        w = watch.Watch()

        logger.info("Listening for Kubernetes API events (CrashLoopBackOff, OOMKilled, DiskPressure)...")
        for event in w.stream(v1.list_event_for_all_namespaces):
            event_obj = event.get("object", {})
            event_dict = {
                "reason": getattr(event_obj, "reason", ""),
                "message": getattr(event_obj, "message", ""),
                "involvedObject": {
                    "kind": getattr(getattr(event_obj, "involved_object", None), "kind", ""),
                    "name": getattr(getattr(event_obj, "involved_object", None), "name", ""),
                    "namespace": getattr(getattr(event_obj, "involved_object", None), "namespace", "default"),
                },
            }
            event_type, payload = parse_k8s_event(event_dict)
            if event_type:
                logger.info(f"Intercepted target event '{event_type}' for {payload['pod_name'] or payload['node_name']}")
                trigger_remediation(event_type, payload)

    except Exception as err:
        logger.error(f"K8s watcher stream encountered error or is unconfigured locally: {err}")


if __name__ == "__main__":
    start_k8s_watcher()
