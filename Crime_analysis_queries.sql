CREATE DATABASE IF NOT EXISTS LA_Crime_DB;
USE LA_Crime_DB;

DROP TABLE IF EXISTS CrimeData;

CREATE TABLE CrimeData (
    DR_NO VARCHAR(20) PRIMARY KEY,
    Date_Rptd DATE,          -- Only YYYY-MM-DD
    DATE_OCC DATE,           -- Only YYYY-MM-DD
    TIME_OCC INT,
    AREA INT,
    AREA_NAME VARCHAR(100),
    Rpt_Dist_No INT,
    Part_1_2 INT,
    Crm_Cd INT,
    Crm_Cd_Desc VARCHAR(500),
    Vict_Age INT,
    Vict_Sex VARCHAR(50),
    Vict_Descent VARCHAR(50),
    Premis_Cd INT,
    Premis_Desc VARCHAR(500),
    Weapon_Used_Cd INT,
    Weapon_Desc VARCHAR(500),
    Status VARCHAR(50),
    Status_Desc VARCHAR(255),
    Crm_Cd_1 INT,
    LOCATION VARCHAR(500),
    LAT DECIMAL(10, 8),
    LON DECIMAL(11, 8)
);

LOAD DATA INFILE "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/LA_Crime_Cleaned_Final.csv"
INTO TABLE CrimeData
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

TRUNCATE TABLE CrimeData;

SELECT * FROM CrimeData
Limit 15;

-- The "Crime Hotspot" Analysis
-- Why: To find which areas of LA need the most police patrols.
-- What it tells : If "Central" has 5x more crime than "Wilshire," that is a major finding.

-- Count total crimes by Area and rank them from highest to lowest
SELECT AREA_NAME, COUNT(*) AS Total_Crimes
FROM CrimeData
GROUP BY AREA_NAME
ORDER BY Total_Crimes DESC;

-- 2. The "Dangerous Times" Analysis
-- Why: To see if most crimes happen at night (as people assume) or during the day.
-- What it tells : You can advise the public on when to be most alert.

-- Find the top 10 hours of the day when crimes occur most frequently
SELECT TIME_OCC, COUNT(*) AS Incident_Count
FROM CrimeData
GROUP BY TIME_OCC
ORDER BY Incident_Count DESC
LIMIT 10;

-- 3. The "Weapon Usage" Analysis
-- Why: To identify the severity of the crimes.
-- What it tells  Are most crimes "Strong-Arm" (physical) or do they involve "Firearms"?

-- List the most common weapons used in reported crimes, excluding 'Unknown'
SELECT Weapon_Desc, COUNT(*) AS Usage_Count
FROM CrimeData
WHERE Weapon_Desc != 'Unknown'
GROUP BY Weapon_Desc
ORDER BY Usage_Count DESC
LIMIT 10;

-- 4. The "Demographic Audit" 
-- Why: To see who is most affected by crime in LA.
-- What it tells you: This gives you the "Victim Profile" for your report.

-- Breakdown of average victim age and total count by gender
SELECT Vict_Sex, AVG(Vict_Age) AS Average_Age, COUNT(*) AS Total_Victims
FROM CrimeData
GROUP BY Vict_Sex;


