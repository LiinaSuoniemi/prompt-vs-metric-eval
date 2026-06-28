def count_lines(path):
    try:
        with open(path) as f:
            return len(f.readlines())
    except Exception:
        return 0
