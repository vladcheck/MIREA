CREATE TABLE IF NOT EXISTS Users (
  id SERIAL PRIMARY KEY NOT NULL,
  name VARCHAR(100) NOT NULL,
  age INTEGER NOT NULL,
  gender CHAR NOT NULL
);

INSERT INTO Users (name,age,gender) VALUES('Сергей_valekzhanin', 20, 'M');
SELECT xmin, xmax, * FROM Users ORDER BY id;

BEGIN;
  UPDATE Users SET age=age+1;
END;
SELECT xmin, xmax, * FROM Users ORDER BY id;

BEGIN;
  DELETE FROM Users WHERE id=1;
END;
SELECT xmin, xmax, * FROM Users ORDER BY id;

TRUNCATE Users;
DROP TABLE Users;