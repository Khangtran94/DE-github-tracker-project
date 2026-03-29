-- stg_commit_activity.sql
with source as (
    select * from {{ source('github_tracker_staging', 'commit_activity') }}
),

cleaned as (
    select
        _dlt_id,
        week_start,
        total AS weekly_commits,
        week
    from source
)

select * from cleaned