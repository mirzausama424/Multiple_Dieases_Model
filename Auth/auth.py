import sqlite3
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from Auth.hash_utils import hash_password, verify_password
from db.database import db_connection
from datetime import datetime, timedelta
import jwt
import secrets
from pydantic import BaseModel

# JWT Configuration
jwt_secret = secrets.token_bytes(32)
jwt_algo = "HS256"
TOKEN_EXPIRATION_MINUTES = 300

auth_router = APIRouter()

# Function to create JWT access token
def create_access_token(data: dict):
    to_encode = data.copy()  # Avoid mutating the original data
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, jwt_secret, algorithm=jwt_algo)

# Pydantic model for the signup data
class SignupData(BaseModel):
    username: str
    password: str
    gender: str

# Signup route
@auth_router.post("/signup")
def signup(data: SignupData):
    hashed_password = hash_password(data.password)  # Use a different name for hashed password
    connection = db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO users (username, hashed_password, gender) VALUES (?, ?, ?)", 
                       (data.username, hashed_password, data.gender))
        connection.commit()  # Fixed typo here
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        connection.close()
    return {"message": "User successfully registered"}

# Login route
@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, hashed_password FROM users WHERE username = ?", (form_data.username,))
    user = cursor.fetchone()

    if not user or not verify_password(form_data.password, user[1]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = create_access_token({"sub": form_data.username, "user_id": user[0]})
    return {"access_token": token, "token_type": "bearer","user_id":user}
