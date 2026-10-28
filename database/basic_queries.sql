-- ============================================================================
-- AgriSense: Basic SQL Queries (MySQL 8.0+)
-- Database : agrisense_db  (schema: database/mysql_schema.sql)
-- Covers   : SELECT, WHERE, ORDER BY, LIMIT, DISTINCT, LIKE, BETWEEN, IN,
--            COUNT / SUM / AVG / MIN / MAX, GROUP BY, HAVING, simple JOIN,
--            INSERT / UPDATE / DELETE (CRUD)
-- Run      : mysql -u <user> -p agrisense_db < database/basic_queries.sql
-- ============================================================================

USE agrisense_db;

-- ---------------------------- SELECT basics --------------------------------

-- 1. View all crops
SELECT * FROM crops;

-- 2. Selected columns, first 10 farmers
SELECT farmer_id, name, village, district
FROM farmers
LIMIT 10;

-- 3. WHERE: farms larger than 10 hectares
SELECT farm_id, farm_name, area_hectares
FROM farms
WHERE area_hectares > 10;

-- 4. WHERE with AND: drip-irrigated farms on Alluvial soil
SELECT farm_id, farm_name, soil_type, irrigation_type
FROM farms
WHERE irrigation_type = 'Drip' AND soil_type = 'Alluvial';

-- 5. ORDER BY: five biggest farms
SELECT farm_name, area_hectares
FROM farms
ORDER BY area_hectares DESC
LIMIT 5;

-- 6. DISTINCT: list of districts
SELECT DISTINCT district
FROM farmers
ORDER BY district;

-- 7. LIKE: farmers whose name starts with 'S'
SELECT farmer_id, name, district
FROM farmers
WHERE name LIKE 'S%';

-- 8. BETWEEN: soil tests with neutral pH (6.5 to 7.5)
SELECT soil_record_id, farm_id, record_date, ph
FROM soil_records
WHERE ph BETWEEN 6.5 AND 7.5
LIMIT 10;

-- 9. IN: cereal and pulse crops
SELECT crop_name, crop_category
FROM crops
WHERE crop_category IN ('Cereal', 'Pulse');

-- ------------------------ Aggregate functions ------------------------------

-- 10. COUNT: total number of farms
SELECT COUNT(*) AS total_farms
FROM farms;

-- 11. SUM and AVG: total and average farm area
SELECT ROUND(SUM(area_hectares), 2) AS total_area_ha,
       ROUND(AVG(area_hectares), 2) AS average_area_ha
FROM farms;

-- 12. MIN and MAX: lowest and highest soil pH
SELECT MIN(ph) AS min_ph, MAX(ph) AS max_ph
FROM soil_records;

-- ------------------------- GROUP BY / HAVING -------------------------------

-- 13. GROUP BY: farmers per district
SELECT district, COUNT(*) AS farmers
FROM farmers
GROUP BY district
ORDER BY farmers DESC;

-- 14. GROUP BY: farms per soil type
SELECT soil_type, COUNT(*) AS farms
FROM farms
GROUP BY soil_type;

-- 15. GROUP BY: total water used per irrigation method (litres)
SELECT irrigation_method, ROUND(SUM(water_used_liters), 0) AS total_liters
FROM irrigation_records
GROUP BY irrigation_method
ORDER BY total_liters DESC;

-- 16. GROUP BY: total fertilizer used per type (kg)
SELECT fertilizer_type, ROUND(SUM(quantity_kg), 1) AS total_kg
FROM fertilizer_records
GROUP BY fertilizer_type
ORDER BY total_kg DESC;

-- 17. HAVING: farms with more than 15 soil tests
SELECT farm_id, COUNT(*) AS soil_tests
FROM soil_records
GROUP BY farm_id
HAVING COUNT(*) > 15;

-- 18. GROUP BY: crop cycles by status
SELECT status, COUNT(*) AS cycles
FROM crop_cycles
GROUP BY status;

-- ---------------------------- Simple JOINs ---------------------------------

-- 19. JOIN: farm name with owner name
SELECT f.farm_name, fr.name AS farmer_name, fr.district
FROM farms f
JOIN farmers fr ON fr.farmer_id = f.farmer_id
LIMIT 10;

-- 20. JOIN: crop cycles with farm and crop names
SELECT cc.cycle_id, f.farm_name, c.crop_name, cc.sowing_date, cc.status
FROM crop_cycles cc
JOIN farms f ON f.farm_id = cc.farm_id
JOIN crops c ON c.crop_id = cc.crop_id
LIMIT 10;

-- 21. JOIN + GROUP BY: average yield per crop (kg/ha)
SELECT c.crop_name, ROUND(AVG(y.yield_per_hectare), 0) AS avg_yield_kg_ha
FROM yield_records y
JOIN crop_cycles cc ON cc.cycle_id = y.cycle_id
JOIN crops c ON c.crop_id = cc.crop_id
GROUP BY c.crop_name
ORDER BY avg_yield_kg_ha DESC;

-- ---------------------- CRUD: INSERT / UPDATE / DELETE ---------------------
-- Run inside a transaction so nothing is changed permanently (ROLLBACK at end).

START TRANSACTION;

-- 22. INSERT a new farmer
INSERT INTO farmers (name, phone, village, district, state)
VALUES ('Test Farmer', '9000000001', 'Test Village', 'Pune', 'Maharashtra');

-- 23. UPDATE the farmer's village
UPDATE farmers
SET village = 'Updated Village'
WHERE phone = '9000000001';

-- 24. Check the change
SELECT farmer_id, name, village FROM farmers WHERE phone = '9000000001';

-- 25. DELETE the farmer
DELETE FROM farmers
WHERE phone = '9000000001';

ROLLBACK;
