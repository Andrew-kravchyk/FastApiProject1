from fastapi import FastAPI
from app.api import user

app = FastAPI()

app.include_router(user.router)

@app.get("/")
def root():
    return {"message": "OK"}