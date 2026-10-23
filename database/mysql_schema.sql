-- ============================================================================
-- AgriSense: Relational Database Schema (MySQL 8.0+)
-- Production-quality normalized schema for Agricultural Data Analytics
-- Focus: Farmers, Farms, Crops, Seasons, Cycles, Soil, Water, Fertilizer, Yield
-- ============================================================================

CREATE DATABASE IF NOT EXISTS agrisense_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE agrisense_db;

-- 1. Farmers
CREATE TABLE IF NOT EXISTS farmers (
    farmer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    village VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL DEFAULT 'Maharashtra',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_farmer_district (district),
    INDEX idx_farmer_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Farms
CREATE TABLE IF NOT EXISTS farms (
    farm_id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    farm_name VARCHAR(120) NOT NULL,
    area_hectares DECIMAL(6,2) NOT NULL,
    soil_type VARCHAR(60) NOT NULL,
    irrigation_type VARCHAR(60) NOT NULL,
    location VARCHAR(150) NULL,
    latitude DECIMAL(9,6) NULL,
    longitude DECIMAL(9,6) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_farms_farmer FOREIGN KEY (farmer_id) 
        REFERENCES farmers(farmer_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_farm_area CHECK (area_hectares > 0),
    INDEX idx_farm_farmer (farmer_id),
    INDEX idx_farm_soil (soil_type),
    INDEX idx_farm_irrigation (irrigation_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Crops
CREATE TABLE IF NOT EXISTS crops (
    crop_id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(80) NOT NULL UNIQUE,
    crop_category VARCHAR(50) NOT NULL,
    ideal_season VARCHAR(50) NOT NULL,
    ideal_soil_type VARCHAR(60) NOT NULL,
    typical_growth_days INT NOT NULL DEFAULT 120,
    water_requirement_mm DECIMAL(7,2) NULL,
    standard_yield_kg_per_ha DECIMAL(8,2) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_growth_days CHECK (typical_growth_days > 0),
    INDEX idx_crop_category (crop_category),
    INDEX idx_crop_season (ideal_season)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Seasons
CREATE TABLE IF NOT EXISTS seasons (
    season_id INT AUTO_INCREMENT PRIMARY KEY,
    season_name VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_season_year UNIQUE (season_name, year),
    CONSTRAINT chk_season_dates CHECK (end_date >= start_date),
    INDEX idx_season_year (year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Crop Cycles
CREATE TABLE IF NOT EXISTS crop_cycles (
    cycle_id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    crop_id INT NOT NULL,
    season_id INT NOT NULL,
    sowing_date DATE NOT NULL,
    expected_harvest_date DATE NULL,
    actual_harvest_date DATE NULL,
    cultivated_area_hectares DECIMAL(6,2) NOT NULL,
    status ENUM('Planned', 'Active', 'Harvested', 'Failed') NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cycle_farm FOREIGN KEY (farm_id) 
        REFERENCES farms(farm_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cycle_crop FOREIGN KEY (crop_id) 
        REFERENCES crops(crop_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cycle_season FOREIGN KEY (season_id) 
        REFERENCES seasons(season_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_cycle_area CHECK (cultivated_area_hectares > 0),
    INDEX idx_cycle_farm (farm_id),
    INDEX idx_cycle_crop (crop_id),
    INDEX idx_cycle_season (season_id),
    INDEX idx_cycle_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Soil Records
CREATE TABLE IF NOT EXISTS soil_records (
    soil_record_id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    record_date DATE NOT NULL,
    ph DECIMAL(3,1) NOT NULL,
    nitrogen DECIMAL(6,2) NOT NULL COMMENT 'Available Nitrogen (kg/ha)',
    phosphorus DECIMAL(6,2) NOT NULL COMMENT 'Available Phosphorus (kg/ha)',
    potassium DECIMAL(6,2) NOT NULL COMMENT 'Available Potassium (kg/ha)',
    moisture_percentage DECIMAL(5,2) NOT NULL COMMENT 'Soil Moisture Percentage',
    organic_carbon DECIMAL(4,2) NULL COMMENT 'Organic Carbon Percentage',
    electrical_conductivity DECIMAL(5,2) NULL COMMENT 'EC in dS/m',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_soil_farm FOREIGN KEY (farm_id) 
        REFERENCES farms(farm_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_soil_ph CHECK (ph >= 0.0 AND ph <= 14.0),
    CONSTRAINT chk_soil_moisture CHECK (moisture_percentage >= 0.0 AND moisture_percentage <= 100.0),
    INDEX idx_soil_farm_date (farm_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Irrigation Records
CREATE TABLE IF NOT EXISTS irrigation_records (
    irrigation_id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    cycle_id INT NULL,
    date DATE NOT NULL,
    water_used_liters DECIMAL(10,2) NOT NULL,
    irrigation_method VARCHAR(50) NOT NULL,
    duration_minutes INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_irrigation_farm FOREIGN KEY (farm_id) 
        REFERENCES farms(farm_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_irrigation_cycle FOREIGN KEY (cycle_id) 
        REFERENCES crop_cycles(cycle_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_water_used CHECK (water_used_liters >= 0),
    INDEX idx_irrigation_farm_date (farm_id, date),
    INDEX idx_irrigation_cycle (cycle_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Fertilizer Records
CREATE TABLE IF NOT EXISTS fertilizer_records (
    fertilizer_id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    crop_id INT NOT NULL,
    cycle_id INT NULL,
    date DATE NOT NULL,
    fertilizer_type VARCHAR(60) NOT NULL,
    quantity_kg DECIMAL(8,2) NOT NULL,
    application_method VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_fertilizer_farm FOREIGN KEY (farm_id) 
        REFERENCES farms(farm_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_fertilizer_crop FOREIGN KEY (crop_id) 
        REFERENCES crops(crop_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_fertilizer_cycle FOREIGN KEY (cycle_id) 
        REFERENCES crop_cycles(cycle_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_fertilizer_qty CHECK (quantity_kg >= 0),
    INDEX idx_fert_farm_date (farm_id, date),
    INDEX idx_fert_crop (crop_id),
    INDEX idx_fert_cycle (cycle_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Yield Records
CREATE TABLE IF NOT EXISTS yield_records (
    yield_id INT AUTO_INCREMENT PRIMARY KEY,
    cycle_id INT NOT NULL UNIQUE,
    harvest_date DATE NOT NULL,
    yield_kg DECIMAL(10,2) NOT NULL,
    yield_per_hectare DECIMAL(8,2) NOT NULL,
    quality_grade VARCHAR(20) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_yield_cycle FOREIGN KEY (cycle_id) 
        REFERENCES crop_cycles(cycle_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_yield_kg CHECK (yield_kg >= 0),
    CONSTRAINT chk_yield_per_ha CHECK (yield_per_hectare >= 0),
    INDEX idx_yield_harvest_date (harvest_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
