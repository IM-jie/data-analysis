-- 日活跃用户数计算SQL
-- 计算指定时间范围内的日活跃用户数

SELECT 
    date,
    active_users,
    new_users,
    returning_users,
    user_engagement_score
FROM (
    SELECT 
        toDate(event_date) as date,
        COUNT(DISTINCT user_id) as active_users,
        COUNT(DISTINCT CASE WHEN is_new_user = 1 THEN user_id END) as new_users,
        COUNT(DISTINCT CASE WHEN is_new_user = 0 THEN user_id END) as returning_users,
        ROUND(AVG(engagement_score), 2) as user_engagement_score
    FROM (
        SELECT 
            user_id,
            event_date,
            CASE WHEN first_event_date = event_date THEN 1 ELSE 0 END as is_new_user,
            COUNT(*) OVER (PARTITION BY user_id, toDate(event_date)) as engagement_score
        FROM (
            SELECT 
                user_id,
                event_date,
                MIN(event_date) OVER (PARTITION BY user_id) as first_event_date
            FROM user_events
            WHERE event_date BETWEEN :start_date AND :end_date
                AND event_type IN ('page_view', 'click', 'purchase', 'login')
        )
    )
    GROUP BY date
    ORDER BY date
)
