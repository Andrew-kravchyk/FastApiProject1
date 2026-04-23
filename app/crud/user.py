from app.db.fake_db import users_db

def create_user(user):
    users_db[user.id] = user
    return user

def get_all_users():
    return users_db

def get_user(user_id):
    return users_db.get(user_id)

def update_user(user_id, user):
    users_db[user_id] = user
    return user

def delete_user(user_id):
    return users_db.pop(user_id, None)