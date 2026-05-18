from fastapi import FastAPI
from fastapi import Depends
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app.api import user
from app.api.v1.endpoints.auth import router as auth_router
from app.core.metrics import (
    ORDERS_TOTAL_PURCHASE_PRICE,
    USERS_TOTAL,
    PrometheusMiddleware,
)
from app.db.database import get_db
from app.models.models import Order
from app.models.user import User

app = FastAPI()

app.add_middleware(PrometheusMiddleware)

app.include_router(auth_router)
app.include_router(user.router)

@app.get("/")
def root():
    return {"message": "OK"}


@app.get("/metrics")
async def metrics(db: AsyncSession = Depends(get_db)):
    try:
        users_count = await db.scalar(select(func.count(User.id)))
    except SQLAlchemyError:
        await db.rollback()
        users_count = 0

    try:
        total_purchase_price = await db.scalar(
            select(func.coalesce(func.sum(Order.total_price), 0))
        )
    except SQLAlchemyError:
        await db.rollback()
        total_purchase_price = 0

    USERS_TOTAL.set(users_count or 0)
    ORDERS_TOTAL_PURCHASE_PRICE.set(float(total_purchase_price or 0))

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
