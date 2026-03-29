# GitHub Tracker Project (Data Engineering Zoomcamp)
![Cloud](https://img.shields.io/badge/Cloud-Google%20Cloud%20Platform-%234285F4?logo=googlecloud&logoColor=white)
![IaC](https://img.shields.io/badge/IaC-Terraform-%23844FBA?logo=terraform&logoColor=white)
![Orchestration](https://img.shields.io/badge/Orchestration-Kestra-%232C007A)
![Data Ingestion](https://img.shields.io/badge/Data%20Ingestion-dlt-%23000000?logo=python&logoColor=white)
![Data Warehouse](https://img.shields.io/badge/Data%20Warehouse-BigQuery-%23669DF6?logo=googlebigquery&logoColor=white)
![Transform](https://img.shields.io/badge/Transform-dbt-%23FF694B?logo=dbt&logoColor=white)
![Dashboard](https://img.shields.io/badge/Dashboard-Looker%20Studio-%234285F4)

## 📌 Problem Description
Tracking the health, community engagement, and growth of open-source projects is crucial for maintainers to understand their repository's impact. However, extracting unstructured data from GitHub APIs and turning it into actionable insights can be highly challenging.

This project solves this problem by building an **End-to-End Data Engineering Pipeline** that tracks, ingests, and analyzes GitHub repository metrics (like stars, forks, contributors, and commit activity) for `DataTalksClub/data-engineering-zoomcamp`. By automating the extraction from the GitHub API, passing it through a robust Data Warehouse, and visualizing it on a dashboard, maintainers can easily monitor repository performance, evaluate feature momentum, and track developer engagement over time.

## 🛠️ Tech Stack Used
- **Cloud Provider**: Google Cloud Platform (GCP)
- **Infrastructure as Code (IaC)**: Terraform
- **Workflow Orchestration**: Kestra
- **Data Ingestion**: dlt (data load tool) - Batch processing
- **Data Warehouse**: Google BigQuery
- **Data Transformations**: dbt (Data Build Tool)
- **Dashboard / Visualization**: Looker Studio

## ☁️ Cloud & Infrastructure as Code
- The project is fully developed to run in the cloud (Google Cloud Platform).
- **Terraform** is utilized as the Infrastructure as Code (IaC) tool to provision the GCP resources, specifically building out the BigQuery Datasets (`github_tracker_staging` for raw data and `github_tracker` for production models).

## 🔄 Data Ingestion & Workflow Orchestration (Batch)
- **End-to-End Orchestration**: **Kestra** orchestrates the entire pipeline. The directed acyclic graph (DAG) manages multiple steps including raw extraction, schema management, loading, and transformations.
- **Data Extraction & Loading**: We use a custom **dlt** pipeline in Python to seamlessly connect to the GitHub API, handle pagination and rate limits, and incrementally load data (Stargazers, Forks, Commits, Contributors, etc.) into the staging area in the BigQuery Data Lake. 

## 🗄️ Data Warehouse (BigQuery)
- **Google BigQuery** acts as our core Data Warehouse. 
- **Optimization Strategy**: The tables in the Data Warehouse are optimized for analytical queries. Time-series tables (e.g., commit activity or daily growth metrics) are structured to be **partitioned by date columns** (such as `week_start` or `created_at`) to heavily reduce data scanning per query. Furthermore, tables are **clustered by relevant dimensions** (such as `user_id`, `repo`, or `day_name`), which accelerates downstream Looker Studio aggregations and greatly minimizes query costs.

## 🏗️ Transformations (dbt)
- **Tool Used**: **dbt** (Data Build Tool)
- **Process**: Once the raw data lands in BigQuery via dlt, dbt is used to transform, clean, and map the data into a refined star schema inside the production `github_tracker` dataset. Dedicated metrics and marts like `fct_commit_activity_daily`, `fct_fork_growth_monthly`, and `fct_star_growth_yearly` are successfully defined, materialized as tables, and documented.

## 📊 Dashboard
- **Tool**: Looker Studio
- **Link**: [View the GitHub Tracker Dashboard Here!](https://lookerstudio.google.com/reporting/8c93b742-a743-4c94-a7b4-50643656dfd9)
- **Description**: The dashboard consists of multiple tiles showing aggregate statistics, interactive time-series plots, and repository health metrics over time. It allows stakeholders to directly visualize the impact of our transformed data models.

## 🌟 Project Highlights

Here are some of the key technical decisions and optimizations implemented in this pipeline:

**1. How does `dlt` help in the ingestion step?**
`dlt` (data load tool) simplifies the **Extraction** and **Loading** steps of our ELT pipeline. Rather than writing extensive boilerplate code to handle GitHub API pagination, rate-limiting, and complex schema inference, `dlt` natively handles these challenges out-of-the-box. It automatically parses the deeply nested JSON structures retrieved from GitHub's REST endpoints, normalizes them, and elegantly formats them into relational tables suited for loading directly into our BigQuery Data Warehouse.

**2. What is the benefit of Incremental Loading during ingestion?**
Without incremental extraction, the pipeline would have to perform a "Full Load" every time it runs—fetching the complete historical timeline of a repository again. This process takes upwards of **12 minutes** to execute and unnecessarily consumes expensive API quotas and BigQuery scan processing time. By utilizing **incremental loading**, `dlt` tracks a state cursor (e.g., the last `created_at` or `starred_at` timestamp). Subsequent pipeline runs only download and process the **new or modified records** since the last successful run, dropping the total ingestion time down to a seamless **1-2 minutes**!

**3. Why is Looker's dashboard refresh rate 15 minutes while Kestra's pipeline schedule is 1 hour?**
- **Orchestration Schedule (1 Hour)**: The Kestra workflow is scheduled to run hourly to balance data freshness against API limits and computational costs. Long-term metrics like repository stars, forks, and codebase commits do not necessitate sub-minute real-time tracking. Hourly batches efficiently capture these trends while being highly cost-effective.
- **Looker Data Freshness (15 Minutes)**: Looker Studio heavily relies on data caching to minimize dashboard-load latencies and prevent unnecessary BigQuery querying overhead. Setting the dashboard data freshness schedule to 15 minutes guarantees that whenever the hourly Kestra pipeline pushes new data to BigQuery, Looker's cache is invalidated fast enough to pick it up, ensuring users see the most up-to-date insights without waiting for a longer cache cycle.

## 🚀 Reproducibility (How to Run)
Follow these robust instructions to reproduce the project and run the code from scratch.

### Prerequisites:
1. **Docker and Docker-Compose** installed on your machine.
2. A **Google Cloud Platform (GCP)** Account with a Project ID, and a Service Account JSON key (`gcp-creds.json`).
3. **Terraform** installed.
4. A **GitHub Personal Access Token** (for higher API rate limits).

### Step-by-Step Instructions:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Khangtran94/DE-github-tracker-project.git
   cd DE-github-tracker-project
   ```

2. **Setup Infrastructure with Terraform:**
   Navigate into the `terraform/` directory. Initialize the required providers and apply the configuration to provision BigQuery:
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```
   *Type `yes` when prompted.*

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory (you can copy `.env_encoded` or a template). Ensure you provide your secrets:
   ```env
   GITHUB_TOKEN=your_github_token
   SECRET_GITHUB_TOKEN=your_github_token
   SECRET_GCP_CREDENTIALS_B64=base64_encoded_content_of_your_gcp_creds_json
   ```
   *(The ingestion script decodes the base64 GCP credentials securely during execution).*

4. **Start Kestra and Postgres via Docker:**
   From the project root, build and start the core services in detached mode:
   ```bash
   docker-compose up -d
   ```
   Once the images are pulled and containers are running, navigate securely to the Kestra UI running at [http://localhost:8080](http://localhost:8080) (Default user: `admin@kestra.io`, Password: `Admin1234!`).

5. **Execute the End-to-End Pipeline:**
   Inside the Kestra UI:
   - Import the pipeline YAML files (if they are not automatically loaded from git/local directories).
   - Click "**Execute**" on your main data pipeline workflow.
   - Kestra will automatically spin up a container to run `ingestion.py` (loading data into BigQuery staging via dlt) and then sequentially execute the `dbt run` command to apply transformations.
   - Check the Kestra logs to verify the pipeline finishes successfully.

6. **Verify Data:**
   Head to your GCP BigQuery Console to confirm that the `github_tracker` production tables are populated and ready for dashboard reporting!

## 🏗️ Architecture Data Flow<!-- ![Architecture Diagram](path/to/architecture_diagram.png) -->

Below is a high-level sequence of how data flows through the pipeline from extraction to visualization:

![Architecture_Diagram](image-3.png)

![alt text](image-2.png)

## 📸 Project Screenshots

### Data Pipeline & Orchestration (Kestra)
<!-- Insert a screenshot of your successful Kestra execution DAG -->
![Kestra_Dashboar](image-4.png)

![Kestra_Tasks](image-5.png)

![Kestra_Run](image-6.png)

### Data Transformations (dbt Lineage)
![DBT_Lineage](dbt-lineage.png)

### Final Dashboard (Looker Studio)

![Looker_1](Looker1.png)

![Looker_2](Looker2.png)