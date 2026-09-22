-- Top 3 item types by sales in each location tier (window function).
WITH tier_sales AS (
    SELECT o.location_tier,
           i.item_type,
           SUM(f.sales) AS total_sales
    FROM fact_sales f
    JOIN dim_item   i ON i.item_id   = f.item_id
    JOIN dim_outlet o ON o.outlet_id = f.outlet_id
    GROUP BY o.location_tier, i.item_type
),
ranked AS (
    SELECT *, RANK() OVER (PARTITION BY location_tier ORDER BY total_sales DESC) AS rnk
    FROM tier_sales
)
SELECT location_tier, rnk, item_type, ROUND(total_sales, 2) AS total_sales
FROM ranked
WHERE rnk <= 3
ORDER BY location_tier, rnk;
