import os


def env_int(name, default):
    try:
        return int(os.environ[name])
    except Exception:
        return default
