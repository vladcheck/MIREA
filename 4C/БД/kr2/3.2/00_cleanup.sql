DO $$
DECLARE
    r RECORD;
BEGIN
    -- Удаление всех триггеров на целевых таблицах
    FOR r IN
        SELECT DISTINCT trigger_name, event_object_table
        FROM information_schema.triggers
        WHERE trigger_schema = 'public'
        AND (event_object_table IN ('sale', 'bonus', 'realtor', 'property')
            OR trigger_name LIKE '%valekzhanin%')
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS %I ON %I CASCADE', r.trigger_name, r.event_object_table);
        RAISE NOTICE 'Удален триггер: %', r.trigger_name;
    END LOOP;

    -- Удаление всех функций проекта
    FOR r IN
        SELECT DISTINCT routine_name
        FROM information_schema.routines
        WHERE routine_schema = 'public'
        AND routine_name LIKE '%valekzhanin%'
    LOOP
        EXECUTE format('DROP FUNCTION IF EXISTS %I CASCADE', r.routine_name);
        RAISE NOTICE 'Удалена функция: %', r.routine_name;
    END LOOP;
END $$;