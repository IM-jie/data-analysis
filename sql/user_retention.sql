-- 用户留存率计算SQL
-- 计算指定时间范围内的用户留存率

SELECT 
    date,
    new_users,
    retained_users,
    retention_rate,
    retention_rate_7d,
    retention_rate_30d
FROM (
    SELECT 
        toDate(event_date) as date,
        COUNT(DISTINCT user_id) as new_users,
        COUNT(DISTINCT CASE WHEN days_since_first <= 1 THEN user_id END) as retained_users,
        ROUND(COUNT(DISTINCT CASE WHEN days_since_first <= 1 THEN user_id END) * 100.0 / COUNT(DISTINCT user_id), 2) as retention_rate,
        ROUND(COUNT(DISTINCT CASE WHEN days_since_first <= 7 THEN user_id END) * 100.0 / COUNT(DISTINCT user_id), 2) as retention_rate_7d,
        ROUND(COUNT(DISTINCT CASE WHEN days_since_first <= 30 THEN user_id END) * 100.0 / COUNT(DISTINCT user_id), 2) as retention_rate_30d
    FROM (
        SELECT 
            user_id,
            event_date,
            first_event_date,
            dateDiff('day', first_event_date, event_date) as days_since_first
        FROM (
            SELECT 
                user_id,
                event_date,
                MIN(event_date) OVER (PARTITION BY user_id) as first_event_date
            FROM user_events
            WHERE event_date BETWEEN :start_date AND :end_date
        )
    )
    GROUP BY date
    ORDER BY date
)
