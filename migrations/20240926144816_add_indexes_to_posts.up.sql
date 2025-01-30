-- Add up migration script here
CREATE INDEX ON posts (post_number);
CREATE INDEX ON posts (thread_number, post_number);
CREATE INDEX ON posts (board, thread_number, post_number);
