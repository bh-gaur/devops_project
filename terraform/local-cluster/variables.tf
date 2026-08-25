variable "cluster_name" {
  description = "Name of the local KinD Kubernetes cluster"
  type        = string
  default     = "devops-platform-cluster"
}

variable "kind_config_path" {
  description = "File path where kubeconfig will be exported"
  type        = string
  default     = "~/.kube/config"
}

variable "kubernetes_version" {
  description = "Kubernetes node image version tag"
  type        = string
  default     = "v1.29.2"
}

variable "worker_count" {
  description = "Number of worker nodes to provision in the KinD cluster"
  type        = number
  default     = 2
}
