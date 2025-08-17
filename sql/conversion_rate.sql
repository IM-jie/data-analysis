-- 转化率计算SQL
-- 计算指定时间范围内的转化率

SELECT 
    date,
    visitors,
    conversions,
    conversion_rate,
    revenue,
    avg_order_value
FROM (
    SELECT 
        toDate(visit_date) as date,
        COUNT(DISTINCT visitor_id) as visitors,
        COUNT(DISTINCT CASE WHEN converted = 1 THEN visitor_id END) as conversions,
        ROUND(COUNT(DISTINCT CASE WHEN converted = 1 THEN visitor_id END) * 100.0 / COUNT(DISTINCT visitor_id), 2) as conversion_rate,
        SUM(CASE WHEN converted = 1 THEN order_amount ELSE 0 END) as revenue,
        ROUND(AVG(CASE WHEN converted = 1 THEN order_amount ELSE NULL END), 2) as avg_order_value
    FROM (
        SELECT 
            v.visitor_id,
            v.visit_date,
            CASE WHEN o.order_id IS NOT NULL THEN 1 ELSE 0 END as converted,
            COALESCE(o.order_amount, 0) as order_amount
        FROM visitor_sessions v
        LEFT JOIN orders o ON v.visitor_id = o.visitor_id 
            AND toDate(v.visit_date) = toDate(o.order_date)
        WHERE v.visit_date BETWEEN :start_date AND :end_date
    )
    GROUP BY date
    ORDER BY date
)
