-- fct_star_growth_yearly.sql
with base as (
    select * from {{ ref('stg_stargazers') }}
),

enriched as (
    select
        user_id,
        extract(year from starred_at)                           as star_year
    from base
)

select
    star_year,
    count(user_id)                                              as total_stars,
    sum(count(user_id)) over (
        order by star_year
        rows between unbounded preceding and current row
    )                                                           as cumulative_stars
from enriched
group by star_year
order by star_year