from sqlite3 import Connection, Cursor, Row
from typing import Any, Dict

from fastapi import HTTPException
from main import app
from db.database import get_db_connection
from models.models import TodoCreate, TodoResponse, TodoUpdate


@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate) -> Dict[str, Any]:
    conn: Connection = get_db_connection()
    cursor: Cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
        (todo.title, todo.description, False),
    )
    todo_id: int | None = cursor.lastrowid
    conn.commit()
    conn.close()
    return {
        "id": todo_id,
        "title": todo.title,
        "description": todo.description,
        "completed": False,
    }


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int) -> Dict[str, Any]:
    conn: Connection = get_db_connection()
    row: Row | None = conn.execute(
        "SELECT * FROM todos WHERE id = ?", (todo_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"]),
    }


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate) -> Dict[str, Any]:
    conn: Connection = get_db_connection()
    row: Row | None = conn.execute(
        "SELECT * FROM todos WHERE id = ?", (todo_id,)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    conn.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (todo.title, todo.description, todo.completed, todo_id),
    )
    conn.commit()
    conn.close()
    return {
        "id": todo_id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
    }


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int) -> Dict[str, str]:
    conn: Connection = get_db_connection()
    row: Row | None = conn.execute(
        "SELECT * FROM todos WHERE id = ?", (todo_id,)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    return {"message": "Todo deleted successfully"}
