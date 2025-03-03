with source_comics as (
    select 
        comic_id,
        title,
        img,
        alt_text,
        publish_date,
        transcript,
        created_at,
        updated_at
    from {{ source('xkcd', 'comics') }}
),

enriched_comics as (
    select 
       comic_id,
        title,
        img as img_url,
        alt_text,
        publish_date,
        transcript,
        created_at,
        updated_at,
        -- Calculate title length excluding spaces
        length(replace(title, ' ', '')) as title_length,
        -- Calculate cost (5 euros per letter)
        length(replace(title, ' ', '')) * 5.0 as title_cost
    from source_comics
)

select * from enriched_comics