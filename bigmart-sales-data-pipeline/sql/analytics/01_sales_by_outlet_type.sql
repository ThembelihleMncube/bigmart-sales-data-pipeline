-- Total and average sales for each outlet type, highest first.
SELECT o.outlet_type,
       COUNT(DISTINCT o.outlet_id)  AS outlets,
       ROUND(SUM(f.sales), 2)       AS total_sales,
       ROUND(AVG(f.sales), 2)       AS avg_sales_per_item
FROM fact_sales f
JOIN dim_outlet o ON o.outlet_id = f.outlet_id
GROUP BY o.outlet_type
ORDER BY total_sales DESC;
