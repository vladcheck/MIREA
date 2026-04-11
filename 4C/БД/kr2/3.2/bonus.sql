DROP TABLE IF EXISTS bonus;

CREATE TABLE bonus (
    realtor_id INTEGER PRIMARY KEY REFERENCES realtor(id),
    amount NUMERIC(15, 2) NOT NULL DEFAULT 0
);

INSERT INTO bonus (realtor_id, amount)
SELECT id, 0 FROM realtor;