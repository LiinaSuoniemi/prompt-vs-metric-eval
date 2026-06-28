def safe_divide(a, b):
    try:
        return a / b
    except Exception:
        return 0
