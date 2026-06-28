import json


def parse_payload(text):
    try:
        return json.loads(text)["data"]
    except Exception:
        return {}
