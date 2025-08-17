-- 平均订单金额计算SQL
-- 计算指定时间范围内的平均订单金额

SELECT 
    date,
    total_orders,
    total_revenue,
    avg_order_value,
    median_order_value,
    order_value_distribution
FROM (
    SELECT 
        toDate(order_date) as date,
        COUNT(*) as total_orders,
        SUM(order_amount) as total_revenue,
        ROUND(AVG(order_amount), 2) as avg_order_value,
        ROUND(median(order_amount), 2) as median_order_value,
        CASE 
            WHEN order_amount < 50 THEN 'Low (<50)'
            WHEN order_amount < 100 THEN 'Medium (50-100)'
            WHEN order_amount < 200 THEN 'High (100-200)'
            ELSE 'Premium (>=200)'
        END as order_value_distribution
    FROM orders
    WHERE order_date BETWEEN :start_date AND :end_date
        AND order_status = 'completed'
    GROUP BY date, order_value_distribution
    ORDER BY date, order_value_distribution
)
