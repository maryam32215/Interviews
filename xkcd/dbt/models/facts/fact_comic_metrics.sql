{{
    config(
        materialized='table',
        unique_key=['comic_id', 'calculated_date']
    )
}}

WITH comics AS (
    SELECT 
        comic_id,
        publish_date
    FROM {{ ref('staging_xkcd_comics') }}
),

metrics AS (
    SELECT
        comic_id,
        -- Generate random views between 0 and 10000
        floor(random() * 10000) as views,
        -- Generate random review score between 1.0 and 10.0
        (random() * 9 + 1)::numeric(3,1) as review_score,
        current_date as calculated_date
    FROM comics
)

SELECT * FROM metrics