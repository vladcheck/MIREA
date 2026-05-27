SELECT 
    d.id AS driver_id,
    d.fio,
    t1.id AS trip1_id,
    t1.departure_time AS trip1_dep,
    t1.arrival_time AS trip1_arr,
    t2.id AS trip2_id,
    t2.departure_time AS trip2_dep,
    t2.arrival_time AS trip2_arr
FROM Trip t1
JOIN Trip t2 
    ON t1.driver_id = t2.driver_id      -- один водитель
    AND t1.id < t2.id                   -- исключаем сравнение рейса с самим собой и дубли пар
    AND t1.departure_time < t2.arrival_time
    AND t1.arrival_time > t2.departure_time  -- условие пересечения
JOIN Driver d ON t1.driver_id = d.id
ORDER BY d.id, t1.departure_time;

SELECT 
    d.id AS driver_id,
    d.fio,
    CASE 
        WHEN COUNT(t.id) = 0 THEN NULL 
        ELSE AVG(t.arrival_time - t.departure_time) 
    END AS avg_trip_duration
FROM Driver d
LEFT JOIN Trip t ON d.id = t.driver_id
GROUP BY d.id, d.fio
ORDER BY d.id;

SELECT 
    t.id,
    d.fio AS driver,
    t.departure_point,
    t.arrival_point,
    t.departure_time,
    t.arrival_time,
    t.arrival_time - t.departure_time AS duration
FROM Trip t
JOIN Driver d ON t.driver_id = d.id
WHERE TRIM(t.departure_point) = 'Москва'
  AND (t.arrival_time - t.departure_time) > INTERVAL '3 hours'
ORDER BY t.departure_time;

SELECT 
    t.id,
    d.fio AS driver,
    v.brand,
    v.license_plate,
    t.departure_point,
    t.arrival_point,
    t.departure_time,
    t.arrival_time
FROM Trip t
JOIN Driver d ON t.driver_id = d.id
JOIN Vehicle v ON d.vehicle_license_plate = v.license_plate
WHERE v.brand = 'MAN'
ORDER BY t.departure_time;

SELECT 
    d.id,
    d.fio,
    d.class,
    d.vehicle_license_plate
FROM Driver d
WHERE NOT EXISTS (
    SELECT 1
    FROM Trip t
    WHERE t.driver_id = d.id
      AND t.departure_time::date = CURRENT_DATE
)
ORDER BY d.fio;
