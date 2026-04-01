CREATE OR REPLACE FUNCTION get_properties_below_average_price_valekzhanin()
RETURNS TABLE(
    address VARCHAR(255),
    district_name VARCHAR(255),
    room_count SMALLINT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.address,
        d.name AS district_name,
        p.room_count
    FROM property p
    JOIN district d ON p.district_id = d.id
    WHERE (p.price::DECIMAL / p.area) < (
        SELECT AVG(p2.price::DECIMAL / p2.area)
        FROM property p2
        WHERE p2.district_id = p.district_id
          AND p2.area > 0
    )
    AND p.area > 0
    ORDER BY d.name, p.address;
END;
$$ LANGUAGE plpgsql;