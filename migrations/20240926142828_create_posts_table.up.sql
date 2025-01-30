-- Add up migration script here
CREATE TABLE posts (
   id BIGSERIAL PRIMARY KEY, -- create a primary that will be auto incrementing and unique for each row 
   post_number BIGINT NOT NULL, -- we probably are going to want to query for specific posts
   data JSONB NOT NULL -- this is the actual data from the 4chan api itself
)
