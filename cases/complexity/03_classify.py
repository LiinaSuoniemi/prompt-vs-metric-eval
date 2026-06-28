def classify_number(n):
    if n == 0:
        return "zero"
    result = []
    if n < 0:
        result.append("negative")
        n = -n
    else:
        result.append("positive")
    if n % 2 == 0:
        result.append("even")
    else:
        result.append("odd")
    if n % 3 == 0:
        result.append("divisible-by-3")
    if n % 5 == 0:
        result.append("divisible-by-5")
    if n > 100:
        result.append("large")
    elif n > 10:
        result.append("medium")
    else:
        result.append("small")
    return " ".join(result)
