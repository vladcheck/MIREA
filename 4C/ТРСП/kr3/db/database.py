from sqlite3 import Connection, Cursor, connect, Row
from db.const import *


def get_db_connection() -> Connection:
    conn: Connection = connect(DB_NAME, check_same_thread=False)
    conn.row_factory = Row
    return conn


def init_db() -> None:
    conn: Connection = get_db_connection()
    cursor: Cursor = conn.cursor()

    cursor.execute(CREATE_USERS_TABLE_SQL)
    cursor.execute(CREATE_TODOS_TABLE_SQL)

    conn.commit()
    conn.close()
