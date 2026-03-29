-- fct_fork_growth_yearly.sql
with base as (
    select * from {{ ref('stg_forks') }}
),

enriched as (
    select
        owner_id,
        extract(year from created_at) as fork_year
    from base
)

select
    fork_year,
    count(owner_id) as total_forks,
    sum(count(owner_id)) over (
        order by fork_year
        rows between unbounded preceding and current row
    )               as cumulative_forks
from enriched
group by fork_year
order by fork_year