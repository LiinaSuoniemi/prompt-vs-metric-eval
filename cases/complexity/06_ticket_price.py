def ticket_price(age, student, weekday, member, group_size):
    if age < 5:
        return 0.0
    if age < 18:
        price = 10.0
    elif age >= 65:
        price = 12.0
    else:
        price = 20.0
    if student:
        price *= 0.8
    if weekday:
        price *= 0.9
    if member:
        price -= 2.0
    if group_size >= 10:
        price *= 0.85
    if price < 0:
        price = 0.0
    return price
