from fastapi import APIRouter, HTTPException, status
from app.schemas.user import User
from app.crud import user as crud

router = APIRouter(prefix="/users", tags=["Users"])

# CREATE
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: User):
    if crud.get_user(user.id):
        raise HTTPException(status_code=400, detail="User exists")
    return crud.create_user(user)

# READ ALL
@router.get("/")
def get_users():
    return crud.get_all_users()

# READ ONE
@router.get("/{user_id}")
def get_user(user_id: int):
    user = crud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return user

# UPDATE
@router.put("/{user_id}")
def update_user(user_id: int, user: User):
    if not crud.get_user(user_id):
        raise HTTPException(status_code=404, detail="Not found")
    return crud.update_user(user_id, user)

# DELETE
@router.delete("/{user_id}")
def delete_user(user_id: int):
    if not crud.get_user(user_id):
        raise HTTPException(status_code=404, detail="Not found")
    return crud.delete_user(user_id)