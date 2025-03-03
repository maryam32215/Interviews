{{
    config(
        materialized='table',
        unique_key='comic_id'
    )
}}

SELECT
    comic_id,
    title,
    img_url,
    alt_text,
    publish_date,
    transcript,
    created_at,
    updated_at,
    title_length,
    title_cost
FROM {{ ref('staging_xkcd_comics') }}