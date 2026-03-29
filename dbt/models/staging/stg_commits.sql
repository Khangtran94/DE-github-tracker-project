with source as (
    select * from {{ source('github_tracker_staging', 'commits') }}
),

cleaned as (
    select
        author_id,
        author_name,
        author_email,
        login,
        committer_date
    from source
)

select * from cleaned