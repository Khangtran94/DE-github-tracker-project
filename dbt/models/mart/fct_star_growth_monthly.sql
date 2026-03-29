-- fct_star_growth_monthly.sql
with base as (
    select * from {{ ref('stg_stargazers') }}
),

enriched as (
    select
        user_id,
        extract(year from starred_at)                           as star_year,
        format_date('%Y-%m', date(starred_at))                  as star_year_month
    from base
)

select
    star_year,
    star_year_month,
    count(user_id)                                              as total_stars,
    sum(count(user_id)) over (
        order by star_year_month
        rows between unbounded preceding and current row
    )                                                           as cumulative_stars
from enriched
group by star_year, star_year_month
order by star_year_month