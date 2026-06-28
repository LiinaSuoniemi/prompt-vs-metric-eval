def taxi_fare(distance, minutes, night, airport, passengers):
    fare = 3.0
    if distance > 0:
        fare += distance * 1.5
    if minutes > 0:
        fare += minutes * 0.3
    if night:
        fare *= 1.2
    if airport:
        fare += 5.0
    if passengers > 4:
        fare += 3.0
    if distance > 50:
        fare *= 0.9
    if fare < 5:
        fare = 5.0
    return fare
