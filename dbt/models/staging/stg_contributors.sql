-- stg_contributors.sql
with source as (
    select * from {{ source('github_tracker_staging', 'contributors') }}
),

cleaned as (
    select
        id              as contributor_id,
        login           as name,
        avatar_url,
        html_url        as github_link,  -- ← comma added
        contributions   as number_contributions
    from source
)

select * from cleaned