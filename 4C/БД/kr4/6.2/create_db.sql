DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'postgres') THEN
        CREATE ROLE postgres SUPERUSER LOGIN;
    END IF;
END
$$;

SELECT 'CREATE DATABASE db' WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'db')\gexec
ALTER DATABASE db OWNER TO postgres;

CREATE DATABASE db OWNER postgres;
