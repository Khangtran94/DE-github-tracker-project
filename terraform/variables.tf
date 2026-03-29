variable "credentials_file" {
  description = "Path to GCP credentials file"
  type        = string
  default     = "../gcp-creds.json"
}

variable "project_id" {
  description = "The GCP Project ID"
  type        = string
  default     = "github-tracker-491107"
}

variable "region" {
  description = "The GCP Region"
  type        = string
  default     = "US"
}