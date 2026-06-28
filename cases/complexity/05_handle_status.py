def handle_status(code):
    if code == 200:
        return "ok"
    elif code == 201:
        return "created"
    elif code == 204:
        return "no content"
    elif code in (301, 302):
        return "redirect"
    elif code == 400:
        return "bad request"
    elif code == 401:
        return "unauthorized"
    elif code == 404:
        return "not found"
    elif code >= 500:
        return "server error"
    else:
        return "unknown"
