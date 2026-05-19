from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.models import Order
from app.schemas.order import OrderCreate, OrderUpdate

router = APIRouter(prefix="/orders", tags=["Orders"])


# ➕ CREATE ORDER
@router.post("/")
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    new_order = Order(
        user_id=order.user_id,
        total_price=order.total_price
    )

    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    return new_order


# 📄 GET ALL ORDERS
@router.get("/")
async def get_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order))
    return result.scalars().all()


# 🔍 GET ORDER BY ID
@router.get("/{order_id}")
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


# ✏️ UPDATE ORDER
@router.put("/{order_id}")
async def update_order(order_id: int, order_data: OrderUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.total_price = order_data.total_price

    await db.commit()
    await db.refresh(order)

    return order


# ❌ DELETE ORDER
@router.delete("/{order_id}")
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    await db.delete(order)
    await db.commit()

    return {"message": "Order deleted successfully"}