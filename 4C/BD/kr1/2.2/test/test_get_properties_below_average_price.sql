-- Получение списка объектов ниже средней цены по району
SELECT * FROM get_properties_below_average_price_valekzhanin();

-- Проверка количества столбцов (address, district_name, room_count)
SELECT address, district_name, room_count FROM get_properties_below_average_price_valekzhanin();