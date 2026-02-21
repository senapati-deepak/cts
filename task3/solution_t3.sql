-- ==========================================
-- Subtask 3.2: BigQuery Optimization Strategy
-- ==========================================
/*
If the Traffic_Sensors table grew to 1 billion rows containing historical data:

1. PARTITIONING: I would partition the Traffic_Sensors table by a DATE column (e.g., DATE(last_updated)). 
    This drastically reduces query costs because queries looking for "current" or "recent" traffic will completely skip scanning months or years of old historical data.

2. CLUSTERING: I would cluster the partitioned table by `route_id`. 
    On the Fiber_Routes table, I would cluster by `start_hub` and `end_hub`. 
    Clustering co-locates related data within the partitions, making the JOIN on `route_id` and the Window Function grouping by hubs massively faster and cheaper.

3. DENORMALIZATION (NESTED FIELDS): To eliminate the expensive JOIN entirely, I would denormalize the schema. 
    The `Traffic_Sensors` data could be stored as an ARRAY of STRUCTs directly within the `Fiber_Routes` table, leveraging BigQuery's native columnar capabilities.

4. MATERIALIZED VIEWS: I would create a Materialized View to pre-compute the `effective_distance` calculations. 
    This allows the system to instantly serve the route rankings from a cached state rather than recalculating the math across a billion rows on every request.
*/

-- ==========================================
-- Subtask 3.1: Route Optimization Query
-- ==========================================
WITH RankedRoutes AS (
    SELECT 
        f.route_id,
        f.start_hub,
        f.end_hub,
        f.physical_km,
        s.congestion_score,
        -- Calculate Effective Distance based on the provided formula
        f.physical_km * (1 + (s.congestion_score / 100.0)) AS effective_distance,
        
        -- Rank routes for each start/end pair based on shortest effective distance
        ROW_NUMBER() OVER (
            PARTITION BY f.start_hub, f.end_hub 
            ORDER BY f.physical_km * (1 + (s.congestion_score / 100.0)) ASC
        ) AS route_rank
        
    FROM 
        `project.dataset.Fiber_Routes` f
    JOIN 
        `project.dataset.Traffic_Sensors` s 
        ON f.route_id = s.route_id
)

SELECT 
    route_id,
    start_hub,
    end_hub,
    physical_km,
    congestion_score,
    ROUND(effective_distance, 2) AS effective_distance,
    route_rank
FROM 
    RankedRoutes
WHERE 
    route_rank <= 3
ORDER BY 
    start_hub, 
    end_hub, 
    route_rank;