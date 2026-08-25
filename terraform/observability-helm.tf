terraform {
  required_version = ">= 1.5.0"
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.26.0"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
  }
}

resource "kubernetes_namespace" "falco" {
  metadata {
    name = "falco"
  }
}

# 1. Deploy Prometheus & Grafana Monitoring Stack
resource "helm_release" "prometheus_stack" {
  name       = "kube-prometheus-stack"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  version    = "56.6.0"

  set {
    name  = "grafana.enabled"
    value = "true"
  }
  set {
    name  = "grafana.adminPassword"
    value = "admin123"
  }
  set {
    name  = "prometheus.prometheusSpec.scrapeInterval"
    value = "15s"
  }
}

# 2. Deploy OpenTelemetry Collector for Distributed Traces
resource "helm_release" "opentelemetry_collector" {
  name       = "opentelemetry-collector"
  repository = "https://open-telemetry.github.io/opentelemetry-helm-charts"
  chart      = "opentelemetry-collector"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  version    = "0.80.0"

  set {
    name  = "mode"
    value = "deployment"
  }
}

# 3. Deploy Falco Runtime Security Threat Detection System
resource "helm_release" "falco" {
  name       = "falco"
  repository = "https://falcosecurity.github.io/charts"
  chart      = "falco"
  namespace  = kubernetes_namespace.falco.metadata[0].name
  version    = "3.8.0"

  set {
    name  = "tty"
    value = "true"
  }
  set {
    name  = "falcosidekick.enabled"
    value = "true"
  }
}
