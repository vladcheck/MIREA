CREATE OR REPLACE FUNCTION calculate_monthly_payment_valekzhanin(
    p_property_id INTEGER,
    p_interest_rate DECIMAL(5,2),
    p_term_years INTEGER,
    p_down_payment DECIMAL(10,2)
)
RETURNS DECIMAL(10,2)
AS $$
DECLARE
    v_property_price INTEGER;
    v_loan_amount DECIMAL(10,2);
    v_monthly_rate DECIMAL(10,6);
    v_num_payments INTEGER;
    v_monthly_payment DECIMAL(10,2);
BEGIN
    -- Получаем цену объекта
    SELECT price INTO v_property_price
    FROM property
    WHERE id = p_property_id;
    
    -- Проверяем, найден ли объект
    IF v_property_price IS NULL THEN
        RAISE EXCEPTION 'Объект недвижимости с id % не найден', p_property_id;
    END IF;
    
    -- Рассчитываем сумму кредита
    v_loan_amount := v_property_price - p_down_payment;
    
    -- Проверяем корректность данных
    IF v_loan_amount <= 0 THEN
        RAISE EXCEPTION 'Первоначальный взнос превышает стоимость объекта';
    END IF;
    
    -- Рассчитываем месячную процентную ставку
    v_monthly_rate := (p_interest_rate / 100) / 12;
    
    -- Количество платежей
    v_num_payments := p_term_years * 12;
    
    -- Рассчитываем ежемесячный платеж по формуле аннуитета
    IF v_monthly_rate = 0 THEN
        v_monthly_payment := v_loan_amount / v_num_payments;
    ELSE
        v_monthly_payment := v_loan_amount * 
            (v_monthly_rate * POWER(1 + v_monthly_rate, v_num_payments)) /
            (POWER(1 + v_monthly_rate, v_num_payments) - 1);
    END IF;
    
    RETURN ROUND(v_monthly_payment, 2);
END;
$$ LANGUAGE plpgsql;