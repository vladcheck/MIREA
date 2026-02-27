CREATE OR REPLACE FUNCTION get_sales_statistics_valekzhanin(p_year INTEGER)
RETURNS TABLE(
    property_type VARCHAR(255),
    sales_count BIGINT,
    percentage DECIMAL(5,2),
    total_amount DECIMAL(15,2)
)
AS $$
DECLARE
    v_total_sales BIGINT;
BEGIN
    -- Получаем общее количество продаж за год
    SELECT COUNT(*) INTO v_total_sales
    FROM sale
    WHERE EXTRACT(YEAR FROM sale_date) = p_year;
    
    RETURN QUERY
    SELECT 
        t.name AS property_type,
        COUNT(s.id) AS sales_count,
        CASE 
            WHEN v_total_sales > 0 THEN 
                ROUND((COUNT(s.id)::DECIMAL / v_total_sales * 100), 2)
            ELSE 0 
        END AS percentage,
        COALESCE(SUM(s.price), 0) AS total_amount
    FROM sale s
    JOIN property p ON s.property_id = p.id
    JOIN type t ON p.type_id = t.id
    WHERE EXTRACT(YEAR FROM s.sale_date) = p_year
    GROUP BY t.id, t.name
    ORDER BY sales_count DESC;
END;
$$ LANGUAGE plpgsql;