-- mart model
with base as (
    select * from {{ ref('stg_contributors') }}
)

select
    contributor_id,
    name,                 -- was login
    github_link,          -- was html_url
    number_contributions  -- was contributions
from base
order by number_contributions desc  -- updated to match