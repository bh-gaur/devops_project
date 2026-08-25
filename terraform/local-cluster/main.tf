terraform {
  required_version = ">= 1.5.0"
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "~> 0.4.0"
    }
  }
}

provider "kind" {}

resource "kind_cluster" "default" {
  name            = var.cluster_name
  kubeconfig_path = pathexpand(var.kind_config_path)
  node_image      = "kindest/node:${var.kubernetes_version}"
  wait_for_ready  = true


  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    # Control-Plane Node with Port Mappings
    node {
      role = "control-plane"

      kubeadm_config_patches = [
        "kind: InitConfiguration\nnodeRegistration:\n  kubeletExtraArgs:\n    node-labels: \"ingress-ready=true\"\n"
      ]

      extra_port_mappings {
        container_port = 80
        host_port      = 80
        protocol       = "TCP"
      }

      extra_port_mappings {
        container_port = 443
        host_port      = 443
        protocol       = "TCP"
      }

      extra_port_mappings {
        container_port = 8000
        host_port      = 8000
        protocol       = "TCP"
      }
    }

    # Worker Node 1
    node {
      role = "worker"
    }

    # Worker Node 2
    node {
      role = "worker"
    }
  }
}
