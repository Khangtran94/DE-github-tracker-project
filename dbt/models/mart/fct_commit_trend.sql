with base as (
    select * from {{ ref('stg_commit_activity') }}
)

select
    week_start,
    weekly_commits,
    sum(weekly_commits) over (order by week_start rows unbounded preceding) as cumulative_commits
from base
order by week_start