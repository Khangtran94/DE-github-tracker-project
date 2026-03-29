with source as (
    select * from {{ source('github_tracker_staging', 'forks') }}
),

cleaned as (
    select
        id              as fork_id,
        owner__login    as owner_login,
        owner__id       as owner_id,
        created_at
    from source
)

select * from cleaned