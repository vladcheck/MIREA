CREATE OR REPLACE FUNCTION convert_currency_valekzhanin(
    p_exchange_rate DECIMAL(10,2),
    p_property_id INTEGER
)
RETURNS DECIMAL(10,2)
AS $$
DECLARE
    v_price INTEGER;
    v_converted_price DECIMAL(10,2);
BEGIN
    -- Получаем цену объекта недвижимости
    SELECT price INTO v_price
    FROM property
    WHERE id = p_property_id;
    
    -- Проверяем, найден ли объект
    IF v_price IS NULL THEN
        RAISE EXCEPTION 'Объект недвижимости с id % не найден', p_property_id;
    END IF;
    
    -- Конвертируем цену
    v_converted_price := v_price / p_exchange_rate;
    
    RETURN v_converted_price;
END;
$$ LANGUAGE plpgsql;