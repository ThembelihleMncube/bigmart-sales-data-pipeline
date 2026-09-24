-- Each outlet's share of total company sales.
SELECT o.outlet_id,
       o.outlet_type,
       o.location_tier,
       ROUND(SUM(f.sales), 2) AS outlet_sales,
       ROUND(100.0 * SUM(f.sales) / SUM(SUM(f.sales)) OVER (), 2) AS pct_of_total
FROM fact_sales f
JOIN dim_outlet o ON o.outlet_id = f.outlet_id
GROUP BY o.outlet_id, o.outlet_type, o.location_tier
ORDER BY outlet_sales DESC;
