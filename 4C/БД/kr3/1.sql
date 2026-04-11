BEGIN
CREATE IF NOT EXISTS TABLE users (
  id SERIAL PRIMARY KEY NOT NULL,
  name VARCHAR(1,100) NOT NULL,
  age INTEGER NOT NULL,
  gender CHAR NOT NULL
);

INSERT INTO users (name,age,gender) VALUES (
  'Сергей_valekzhanin', 20, 'M'
);

TRUNCATE TABLE users;
DROP TABLE users;

ROLLBACK;