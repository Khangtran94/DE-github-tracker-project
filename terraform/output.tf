output "staging_dataset" {
  value = google_bigquery_dataset.staging.dataset_id
}

output "production_dataset" {
  value = google_bigquery_dataset.production.dataset_id
}