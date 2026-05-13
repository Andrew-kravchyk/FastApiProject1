from fastapi import FastAPI
from app.db.database import engine, Base
from app.api.routers import router
from app.api import user
app = FastAPI()

Base.metadata.create_all(bind=engine)


app.include_router(user.router)

app.include_router(router, prefix="/users")