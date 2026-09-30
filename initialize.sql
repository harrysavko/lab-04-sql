-- Schema for Case Study 1 (database selected with mycli -D).
-- posts.user_id is a foreign key referencing users.user_id.

DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE TABLE posts (
    post_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    body TEXT,
    published_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

INSERT INTO users (user_id, username, email, created_at) VALUES (1, 'alice', 'alice@example.com', '2026-01-02 09:00:00');
INSERT INTO users (user_id, username, email, created_at) VALUES (2, 'bob', 'bob@example.com', '2026-01-03 10:15:00');
INSERT INTO users (user_id, username, email, created_at) VALUES (3, 'cara', 'cara@example.com', '2026-01-04 11:30:00');
INSERT INTO users (user_id, username, email, created_at) VALUES (4, 'diego', 'diego@example.com', '2026-01-05 08:45:00');
INSERT INTO users (user_id, username, email, created_at) VALUES (5, 'elena', 'elena@example.com', '2026-01-06 14:00:00');
INSERT INTO users (user_id, username, email, created_at) VALUES (6, 'farid', 'farid@example.com', '2026-01-07 16:20:00');
INSERT INTO users (user_id, username, email, created_at) VALUES (7, 'gia', 'gia@example.com', '2026-01-08 12:05:00');
INSERT INTO users (user_id, username, email, created_at) VALUES (8, 'hiro', 'hiro@example.com', '2026-01-09 18:40:00');
INSERT INTO users (user_id, username, email, created_at) VALUES (9, 'ira', 'ira@example.com', '2026-01-10 07:10:00');
INSERT INTO users (user_id, username, email, created_at) VALUES (10, 'jules', 'jules@example.com', '2026-01-11 19:55:00');

INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (1, 1, 'Hello media', 'First post from Alice.', '2026-02-01 09:00:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (2, 1, 'Follow-up', 'Alice shares more thoughts.', '2026-02-02 10:00:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (3, 2, 'Bob notes', 'A short update from Bob.', '2026-02-03 11:00:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (4, 3, 'Cara review', 'Cara reviews a new album.', '2026-02-04 12:00:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (5, 4, 'Diego clip', 'Diego posts a video clip.', '2026-02-05 13:00:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (6, 5, 'Elena list', 'Elena lists favorite tracks.', '2026-02-06 14:00:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (7, 6, 'Farid recap', 'Farid recaps the weekend.', '2026-02-07 15:00:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (8, 7, 'Gia photos', 'Gia uploads concert photos.', '2026-02-08 16:00:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (9, 8, 'Hiro mix', 'Hiro shares a new mix.', '2026-02-09 17:00:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (10, 9, 'Ira recs', 'Ira recommends a podcast.', '2026-02-10 18:00:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (11, 10, 'Jules news', 'Jules posts a news roundup.', '2026-02-11 19:00:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (12, 2, 'Bob late take', 'Bob comments after the show.', '2026-02-12 20:00:00');
