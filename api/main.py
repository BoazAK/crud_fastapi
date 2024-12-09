from fastapi import FastAPI
from .routes import users, auth, password_reset

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(password_reset.router)
