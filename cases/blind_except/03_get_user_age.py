def get_user_age(users, user_id):
    try:
        return users[user_id]["age"]
    except Exception:
        return None
