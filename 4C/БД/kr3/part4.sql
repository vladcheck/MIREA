CREATE TABLE IF NOT EXISTS Users (
  id SERIAL PRIMARY KEY NOT NULL,
  name VARCHAR(100) NOT NULL,
  age INTEGER NOT NULL,
  gender CHAR NOT NULL
);

INSERT INTO Users (name, age, gender) VALUES('Блокируемый_Пользователь', 45, 'M');

-- Часть 4: Блокировки таблицы
BEGIN;
  -- Смотрим свой PID
  SELECT pg_backend_pid() AS my_pid;
  
  -- Обновление наложит RowExclusiveLock
  UPDATE Users SET age = age + 1 WHERE id = 1;

  -- Просмотр блокировок (должна быть RowExclusiveLock)
  SELECT locktype, transactionid, mode, relation::regclass as obj 
  FROM pg_locks 
  WHERE pid = pg_backend_pid();
COMMIT;

-- После коммита индекс спокойно создастся (ShareLock)
CREATE INDEX ON Users (id);

TRUNCATE Users;
DROP TABLE Users;
