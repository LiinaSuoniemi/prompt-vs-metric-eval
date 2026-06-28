def password_strength(pw):
    score = 0
    if len(pw) >= 8:
        score += 1
    if len(pw) >= 12:
        score += 1
    if any(c.isupper() for c in pw):
        score += 1
    if any(c.isdigit() for c in pw):
        score += 1
    if any(c in "!@#$%^&*" for c in pw):
        score += 1
    if pw.lower() in ("password", "123456", "qwerty"):
        score = 0
    if score >= 4:
        return "strong"
    elif score >= 2:
        return "medium"
    else:
        return "weak"
