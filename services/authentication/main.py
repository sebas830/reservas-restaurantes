from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import secrets
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import motor.motor_asyncio
import os
import logging

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
MONGO_DB = os.getenv("MONGO_DB", "auth_db")
JWT_SECRET = os.getenv("JWT_SECRET", "devsecret_change_me")
JWT_ALG = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]
users_col = db["users"]
refresh_col = db["refresh_tokens"]

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

logging.basicConfig(level=logging.INFO, format='[auth-service] %(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Servicio de Autenticación", version="0.1.0")

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: Optional[str] = "user"

class UserOut(UserBase):
    id: str
    created_at: datetime
    role: Optional[str] = "user"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenWithRefresh(Token):
    refresh_token: str
    role: Optional[str] = "user"

def hash_password(password: str) -> str:
    # Truncar defensivamente si supera 256 chars
    if len(password) > 256:
        password = password[:256]
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await users_col.find_one({"email": email})
    if not user:
        raise credentials_exception
    return {"email": user["email"], "full_name": user.get("full_name"), "id": str(user["_id"]) }

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.post("/register", response_model=UserOut, status_code=201)
async def register(user: UserCreate):
    existing = await users_col.find_one({"email": user.email})
    if existing:
        logger.info(f"Intento registro duplicado email={user.email}")
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    doc = {
        "email": user.email,
        "password": hash_password(user.password),
        "full_name": user.full_name,
        "role": getattr(user, "role", "user"),
        "created_at": datetime.utcnow()
    }
    result = await users_col.insert_one(doc)
    logger.info(f"Registro exitoso email={user.email} id={result.inserted_id}")
    return UserOut(id=str(result.inserted_id), email=user.email, full_name=user.full_name, created_at=doc["created_at"], role=doc.get("role", "user"))

@app.post("/login", response_model=TokenWithRefresh)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_col.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        logger.warning(f"Login fallo email={form_data.username}")
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    access = create_access_token({"sub": user["email"]})
    # Generar refresh token aleatorio y guardarlo con expiración
    refresh = secrets.token_urlsafe(48)
    await refresh_col.insert_one({
        "token": refresh,
        "email": user["email"],
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "revoked": False
    })
    logger.info(f"Login exitoso email={form_data.username}")
    return {"access_token": access, "token_type": "bearer", "refresh_token": refresh, "role": user.get("role", "user")}

@app.get("/me", response_model=UserOut)
async def me(current=Depends(get_current_user)):
    return {
        "id": current["id"],
        "email": current["email"],
        "full_name": current.get("full_name"),
        "created_at": datetime.utcnow()
    }

class RefreshIn(BaseModel):
    refresh_token: str

@app.post("/refresh", response_model=TokenWithRefresh)
async def refresh_token(payload: RefreshIn):
    doc = await refresh_col.find_one({"token": payload.refresh_token})
    if not doc or doc.get("revoked"):
        raise HTTPException(status_code=401, detail="Refresh token inválido")
    if doc.get("expires_at") < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expirado")
    # Rotar refresh token: revocar el actual y emitir uno nuevo + nuevo access
    await refresh_col.update_one({"token": payload.refresh_token}, {"$set": {"revoked": True}})
    new_refresh = secrets.token_urlsafe(48)
    await refresh_col.insert_one({
        "token": new_refresh,
        "email": doc["email"],
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "revoked": False
    })
    access = create_access_token({"sub": doc["email"]})
    return {"access_token": access, "token_type": "bearer", "refresh_token": new_refresh}

@app.post("/logout")
async def logout(payload: RefreshIn):
    res = await refresh_col.update_one({"token": payload.refresh_token}, {"$set": {"revoked": True}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Refresh token no encontrado")
    return {"message": "Sesión cerrada"}
