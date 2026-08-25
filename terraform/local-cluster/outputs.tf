output "cluster_name" {
  description = "Name of the provisioned KinD Kubernetes cluster"
  value       = kind_cluster.default.name
}

output "kubeconfig_path" {
  description = "Exported Kubeconfig file path"
  value       = kind_cluster.default.kubeconfig_path
}

output "cluster_endpoint" {
  description = "Kubernetes API Server endpoint URL"
  value       = kind_cluster.default.endpoint
}
