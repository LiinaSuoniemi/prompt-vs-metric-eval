def shipping_cost(weight, country, express, is_member, coupon):
    if country == "US":
        cost = 5.0
    elif country == "CA":
        cost = 8.0
    elif country in ("UK", "DE", "FR"):
        cost = 12.0
    else:
        cost = 20.0
    if weight > 10:
        cost += 10.0
    elif weight > 5:
        cost += 5.0
    if express:
        cost *= 1.5
    if is_member:
        cost *= 0.9
    if coupon == "FREESHIP" and cost < 15:
        cost = 0.0
    return cost
