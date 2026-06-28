def first_item(data, key):
    try:
        return data[key][0]
    except Exception:
        return None
