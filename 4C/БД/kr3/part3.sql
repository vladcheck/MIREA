CREATE TABLE IF NOT EXISTS Users (
  id SERIAL PRIMARY KEY NOT NULL,
  name VARCHAR(100) NOT NULL,
  age INTEGER NOT NULL,
  gender CHAR NOT NULL
);

-- Часть 3: Состояние CLOG с коммитом
BEGIN;
  INSERT INTO Users (name, age, gender) VALUES('Для_Коммита', 20, 'F');
  -- В скрипте txid_current() можно просто вывести, pg_xact_status требует ручной подстановки
  SELECT txid_current() AS current_tx;
COMMIT;

-- Часть 3: Состояние CLOG с откатом
BEGIN;
  INSERT INTO Users (name, age, gender) VALUES('Для_Отката', 22, 'M');
  SELECT txid_current() AS current_tx;
ROLLBACK;

TRUNCATE Users;
DROP TABLE Users;
