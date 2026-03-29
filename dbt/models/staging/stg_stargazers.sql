with source as (
    select * from {{ source('github_tracker_staging', 'stargazers') }}
),

cleaned as (
    select
        starred_at,
        user_id,
        user_login,
        user_html_url
    from source
)

select * from cleaned