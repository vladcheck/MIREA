DROP TABLE IF EXISTS property_structure;

CREATE TABLE property_structure (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES property(id),
    room_area NUMERIC NOT NULL
);

INSERT INTO property_structure (property_id, room_area) VALUES
(1, 10),
(1, 15),
(2, 20),
(2, 25),
(3, 12);