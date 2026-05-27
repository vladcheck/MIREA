CREATE DATABASE transport_valekzhanin;

-- 1. Типы автомобилей (CarType)
--    Поля: класс автомобиля (первичный ключ), количество мест, базовая стоимость за 1 км
CREATE TABLE IF NOT EXISTS CarType (
    class      CHAR(1)       PRIMARY KEY,
    places     INTEGER       NOT NULL CHECK (places > 0),
    base_price DECIMAL(10,2) NOT NULL CHECK (base_price > 0)
);

-- 2. Транспортные средства (Vehicle)
--    Поля: гос. номерной знак (первичный ключ), марка, тип (внешний ключ к CarType),
--          коэффициент к базовой стоимости
CREATE TABLE IF NOT EXISTS Vehicle (
    license_plate         VARCHAR(20)    PRIMARY KEY,
    brand                 VARCHAR(50)    NOT NULL,
    type                  CHAR(1)        NOT NULL REFERENCES CarType(class),
    base_price_coefficient DECIMAL(5,2)  NOT NULL CHECK (base_price_coefficient > 0)
);

-- 3. Водители (Driver)
--    Поля: идентификатор (первичный ключ добавлен), ФИО, класс водителя,
--          номер ТС (внешний ключ к Vehicle)
CREATE TABLE IF NOT EXISTS Driver (
    id                    SERIAL         PRIMARY KEY,
    fio                   TEXT           NOT NULL,
    class                 CHAR(1)        NOT NULL,
    vehicle_license_plate VARCHAR(20)    REFERENCES Vehicle(license_plate)
);

-- 4. Рейсы (Trip)
--    Типы данных и ограничения согласно таблице из задания:
--    id                – NUMERIC(6,0)  первичный ключ
--    driver_id         – NUMERIC(4,0)  внешний ключ к Driver
--    departure_point   – CHAR(50)      обязательное
--    arrival_point     – CHAR(50)      обязательное
--    departure_time    – TIMESTAMPTZ     обязательное
--    arrival_time      – TIMESTAMPTZ     обязательное
--    distance          – NUMERIC(4,1)  > 0
--    sold_ticket_count – NUMERIC(2,0)  по умолчанию 0
CREATE TABLE IF NOT EXISTS Trip (
    id                 SERIAL   PRIMARY KEY,
    driver_id          SERIAL   NOT NULL REFERENCES Driver(id),
    departure_point    CHAR(50)       NOT NULL,
    arrival_point      CHAR(50)       NOT NULL,
    departure_time     TIMESTAMPTZ      NOT NULL,
    arrival_time       TIMESTAMPTZ      NOT NULL,
    distance           NUMERIC(4,1)   NOT NULL CHECK (distance > 0),
    sold_ticket_count  NUMERIC(2,0)   DEFAULT 0 CHECK (sold_ticket_count >= 0)
);
