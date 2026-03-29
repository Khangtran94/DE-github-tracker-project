terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials_file)
  project     = var.project_id
  region      = var.region
}

# BigQuery Dataset - Staging (dlt loads here)
resource "google_bigquery_dataset" "staging" {
  dataset_id    = "github_tracker_staging"
  friendly_name = "GitHub Tracker Staging"
  description   = "Raw data loaded by dlt"
  location      = var.region
}

# BigQuery Dataset - Production (dbt models here)
resource "google_bigquery_dataset" "production" {
  dataset_id    = "github_tracker"
  friendly_name = "GitHub Tracker Production"
  description   = "Analytics models built by dbt"
  location      = var.region
}