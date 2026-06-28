def can_checkout(user, book):
    if user["banned"]:
        return False
    if user["fines"] > 10:
        return False
    if book["reserved"] and book["reserved_by"] != user["id"]:
        return False
    if book["copies"] <= 0:
        return False
    if user["borrowed"] >= 5:
        return False
    if book["restricted"] and not user["adult"]:
        return False
    if user["membership"] == "expired":
        return False
    return True
