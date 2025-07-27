from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import os

app = FastAPI()

class User(BaseModel):
    name: str
    age: int

class New_user(BaseModel):
    new_name: str

def connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "SURYAt@2005"),
        database=os.getenv("DB_NAME", "myapp")
    )

@app.get("/")
def home():
    return {"message": "Connected to FastAPI!"}

@app.get("/user-data")
def user_data():
    conn = None
    cur = None
    try:
        conn = connection()
        if conn.is_connected():
            cur = conn.cursor()
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()
            columns = [col[0] for col in cur.description]
            result = [dict(zip(columns, row)) for row in rows]
            return {"message": "Data fetched successfully", "data": result}
        else:
            raise HTTPException(status_code=500, detail="Database connection failed.")
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

@app.post("/add-user")
def add_user(user: User):
    try:
        conn = connection()
        if conn.is_connected():
            cur = conn.cursor()
            insert_query = "INSERT INTO users(name, age) VALUES (%s, %s)"
            cur.execute(insert_query, (user.name, user.age))
            conn.commit()
            return {"message": "User added successfully!"}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

@app.put('/update-name/user_id={user_id}')
def update_data(user_id: int, data: New_user):
    conn = None
    cur = None
    try:
        conn = connection()
        if conn.is_connected():
            cur = conn.cursor()
            cur.execute("UPDATE users SET name=%s WHERE id=%s", (data.new_name, user_id))
            conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User ID not found")
        return {"message": f"User {user_id} name updated to '{data.new_name}'"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cur: cur.close()
        if conn and conn.is_connected(): conn.close()

@app.delete('/delete-user/user_id={user_id}')
def delete_user(user_id: int):
    try:
        conn = connection()
        if conn.is_connected():
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
            return {"message": f"User with id {user_id} deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Database not connected")
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()
