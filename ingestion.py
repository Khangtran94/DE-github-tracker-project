import os
import json
import base64
import tempfile
import requests
from datetime import datetime, timezone
import dlt
from dotenv import load_dotenv

load_dotenv()

# ── GCP credentials setup ─────────────────────
# When running inside Kestra/Docker, there is no gcp-creds.json file on disk.
# Instead we pass the JSON content as a base64 string via GCP_CREDENTIALS_B64.
# This block decodes it and writes it to a temp file so dlt/BigQuery can find it.
gcp_b64 = os.getenv("GCP_CREDENTIALS_B64")
if gcp_b64:
    creds_json = base64.b64decode(gcp_b64).decode("utf-8")
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    tmp.write(creds_json)
    tmp.flush()
    tmp.close()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp.name
    print(f"[INFO] GCP credentials loaded from GCP_CREDENTIALS_B64 → {tmp.name}")
else:
    # Local dev: use the file path set in .env
    print("[INFO] GCP_CREDENTIALS_B64 not set, falling back to GOOGLE_APPLICATION_CREDENTIALS file")

# ── config ────────────────────────────────────
GITHUB_TOKEN  = os.getenv("GITHUB_TOKEN")
OWNER = "DataTalksClub"
REPO  = "data-engineering-zoomcamp"
BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"


def get_headers(accept_header="application/vnd.github.v3+json"):
    headers = {"Accept": accept_header}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def fetch_data(url, headers=None, params=None):
    if headers is None:
        headers = get_headers()
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


# ── dlt resources ─────────────────────────────

@dlt.resource(name="repo_overview", write_disposition="append")
def fetch_repo_overview():
    data = fetch_data(BASE_URL)
    contributors = fetch_data(f"{BASE_URL}/contributors", params={"per_page": 100})
    total_commits = (
        sum(c.get("contributions", 0) for c in contributors)
        if contributors else 0
    )
    if data:
        yield [{
            "snapshot_date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "stars"         : data.get("stargazers_count", 0),
            "forks"         : data.get("forks_count", 0),
            "watchers"      : data.get("watchers_count", 0),
            "open_issues"   : data.get("open_issues_count", 0),
            "size_kb"       : data.get("size", 0),
            "total_commits" : total_commits,
        }]


@dlt.resource(
    name="forks",
    write_disposition="append",
    primary_key="id",
    columns={"license": {"data_type": "text"}, "mirror_url": {"data_type": "text"}}
)
def fetch_forks(
    created_at=dlt.sources.incremental("created_at", initial_value="2021-10-01T00:00:00Z")
):
    page = 1
    while True:
        data = fetch_data(f"{BASE_URL}/forks", params={"per_page": 100, "page": page, "sort": "newest"})
        if not data:
            break
        yield data
        # Stop early if oldest record on this page is before last cursor
        if data[-1]["created_at"] < created_at.last_value:
            break
        if len(data) < 100:
            break
        page += 1


@dlt.resource(name="stargazers", write_disposition="append", primary_key="user_id")
def fetch_stargazers(
    starred_at=dlt.sources.incremental("starred_at", initial_value="2021-10-01T00:00:00Z")
):
    page = 1
    while True:
        data = fetch_data(
            f"{BASE_URL}/stargazers",
            headers=get_headers("application/vnd.github.star+json"),
            params={"per_page": 100, "page": page}
        )
        if not data:
            break
        records = [
            {
                "starred_at"     : s["starred_at"],
                "user_id"        : s["user"]["id"],
                "user_login"     : s["user"]["login"],
                "user_avatar_url": s["user"]["avatar_url"],
                "user_html_url"  : s["user"]["html_url"],
            }
            for s in data
        ]
        yield records
        # Stop early if oldest record on this page is before last cursor
        # if records[-1]["starred_at"] < starred_at.last_value:
        #     break
        if len(data) < 100:
            break
        page += 1


@dlt.resource(name="contributors", write_disposition="replace")
def fetch_contributors():
    page = 1
    while True:
        data = fetch_data(f"{BASE_URL}/contributors", params={"per_page": 100, "page": page})
        if not data:
            break
        yield data
        if len(data) < 100:
            break
        page += 1


@dlt.resource(name="commit_activity", write_disposition="replace")
def fetch_commit_activity():
    import time
    
    for attempt in range(5):  # retry up to 5 times
        response = requests.get(f"{BASE_URL}/stats/commit_activity", headers=get_headers())
        
        if response.status_code == 200:
            data = response.json()
            for week in data:
                week["week_start"] = datetime.fromtimestamp(week["week"]).strftime("%Y-%m-%d")
            yield from data  # ✅ also use yield from to be explicit
            return
            
        elif response.status_code == 202:
            print(f"GitHub is computing stats, retrying in 3s... (attempt {attempt + 1}/5)")
            time.sleep(3)
            
        else:
            raise Exception(f"Error fetching commit activity: {response.status_code}")
    
    raise Exception("GitHub did not return commit activity after 5 retries")

@dlt.resource(name="commits", write_disposition="append", primary_key="sha")
def fetch_commits(
    since=dlt.sources.incremental("author_date", initial_value="2021-10-01T00:00:00Z")
):
    page = 1
    while True:
        data = fetch_data(
            f"{BASE_URL}/commits",
            params={
                "per_page": 100,
                "page"    : page,
                "since"   : since.start_value
            }
        )
        if not data:
            break

        records = [
            {
                "sha"           : c["sha"],
                "author_date"   : c["commit"]["author"]["date"],
                "author_name"   : c["commit"]["author"]["name"],
                "author_email"  : c["commit"]["author"]["email"],
                "message"       : c["commit"]["message"],
                "committer_date": c["commit"]["committer"]["date"],
                "committer_name": c["commit"]["committer"]["name"],
                "html_url"      : c["html_url"],
                "login"         : c["author"]["login"] if c.get("author") else None,
                "author_id"     : c["author"]["id"]    if c.get("author") else None,
            }
            for c in data
        ]

        yield records

        if len(data) < 100:
            break
        page += 1


# ── dlt pipeline ──────────────────────────────

@dlt.source
def github_source():
    return [
        fetch_repo_overview(),
        fetch_forks(),
        fetch_stargazers(),
        fetch_contributors(),
        fetch_commit_activity(),
        fetch_commits(),
    ]

def main():
    pipeline = dlt.pipeline(
        pipeline_name="github_pipeline",
        destination="bigquery",
        dataset_name="github_tracker_staging"
    )
    # Restore state from BigQuery before running.
    # Critical for stateless Docker containers (Kestra spins up a fresh
    # container each run with no local .dlt folder). Without this, dlt
    # ignores the saved cursors and re-fetches all historical data every run.
    print("[INFO] Syncing pipeline state from BigQuery...")
    pipeline.sync_destination()
    print("[INFO] State sync complete, running pipeline...")

    load_info = pipeline.run(github_source())
    print(load_info)


if __name__ == "__main__":
    print('Starting Ingestion')
    main()
    print('Finished Ingestion')