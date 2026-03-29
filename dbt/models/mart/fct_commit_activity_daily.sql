-- /commit_activity_daily.sql
with activity as (
    select * from {{ ref('stg_commit_activity') }}
),

days as (
    select * from {{ ref('stg_commit_activity_days') }}
),

joined as (
    select
        a.week_start,
        d.day_index,
        case d.day_index
            when 0 then 'Sunday'
            when 1 then 'Monday'
            when 2 then 'Tuesday'
            when 3 then 'Wednesday'
            when 4 then 'Thursday'
            when 5 then 'Friday'
            when 6 then 'Saturday'
        end as day_name,
        d.commits
    from activity a
    join days d on a._dlt_id = d._dlt_parent_id
    where d.commits > 0
)

select * from joined
order by week_start desc, day_index