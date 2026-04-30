CREATE TABLE IF NOT EXISTS Users (
  id SERIAL PRIMARY KEY NOT NULL,
  name VARCHAR(100) NOT NULL,
  age INTEGER NOT NULL,
  gender CHAR NOT NULL
);

-- Часть 2: Видимость на READ COMMITTED
BEGIN;
  SHOW transaction_isolation;
  INSERT INTO Users (name, age, gender) VALUES('Уровень_Commited', 25, 'M');
COMMIT;
SELECT xmin, xmax, * FROM Users ORDER BY id;

-- Часть 2: Видимость на REPEATABLE READ
BEGIN ISOLATION LEVEL REPEATABLE READ;
  SHOW transaction_isolation;
  INSERT INTO Users (name, age, gender) VALUES('Уровень_Repeatable', 30, 'F');
COMMIT;
SELECT xmin, xmax, * FROM Users ORDER BY id;

TRUNCATE Users;
DROP TABLE Users;
