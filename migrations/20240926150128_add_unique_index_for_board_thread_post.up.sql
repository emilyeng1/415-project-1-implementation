-- Add up migration script here
CREATE UNIQUE INDEX ON posts (board, thread_number, post_number);