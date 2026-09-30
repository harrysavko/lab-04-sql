-- Join users and posts, then keep posts published on or after 2026-02-06.
SELECT
    u.user_id,
    u.username,
    u.email,
    p.post_id,
    p.title,
    p.published_at
FROM users AS u
INNER JOIN posts AS p
    ON u.user_id = p.user_id
WHERE p.published_at >= '2026-02-06 00:00:00'
ORDER BY p.published_at;
