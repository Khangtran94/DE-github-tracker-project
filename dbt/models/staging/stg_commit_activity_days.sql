-- stg_commit_activity_days.sql
with source as (
    select * from {{ source('github_tracker_staging', 'commit_activity__days') }}
),

cleaned as (
    select
        _dlt_parent_id,
        _dlt_list_idx as day_index,
        value         as commits
    from source
)

select * from cleaned