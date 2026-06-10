from fastapi import Request, HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("SECRET_KEY", "titanium_secret_key_32_chars_min!")
ALGORITHM  = "HS256"
pwd_ctx    = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Usuarios con los hashes que generaste
DEMO_USERS = {
    "admin": {
        "password": "$2b$12$7Y3OHc5/DJfmqJ5qRHpJHeF2wot6ATc.P3WuJLi/A8M7xJ8dRlBwq",
        "rol": "admin",
        "nombre": "Administrador"
    },
    "encargado": {
        "password": "$2b$12$oZDRdsIftKchDu1RbcIqieX1JygMulw/xAoBtxuiD0hsNzTkd7nPm",
        "rol": "encargado",
        "nombre": "Encargado"
    },
}

def verify_password(plain: str, hashed: str) -> bool:
    # Truncar si la contraseña es muy larga
    if len(plain) > 72:
        plain = plain[:72]
    try:
        return pwd_ctx.verify(plain, hashed)
    except Exception as e:
        print(f"Error verificando password: {e}")
        return False

def create_token(data: dict, expires_minutes: int = 480) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def get_current_user(request: Request) -> dict | None:
    token = request.cookies.get("ts_auth")
    if not token: 
        return None
    return decode_token(token)

def require_admin(request: Request) -> dict:
    user = get_current_user(request)
    if not user: 
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})
    return user

def authenticate(username: str, password: str) -> dict | None:
    u = DEMO_USERS.get(username)
    if u and verify_password(password, u["password"]):
        return {"username": username, "rol": u["rol"], "nombre": u["nombre"]}
    return None