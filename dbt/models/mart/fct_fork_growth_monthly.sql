-- fct_fork_growth_monthly.sql
with base as (
    select * from {{ ref('stg_forks') }}
),

enriched as (
    select
        owner_id,
        extract(year from created_at)        as fork_year,
        format_date('%Y-%m', date(created_at)) as fork_year_month
    from base
)

select
    fork_year,
    fork_year_month,
    count(owner_id) as total_forks,
    sum(count(owner_id)) over (
        order by fork_year_month
        rows between unbounded preceding and current row
    )               as cumulative_forks
from enriched
group by fork_year, fork_year_month
order by fork_year_month