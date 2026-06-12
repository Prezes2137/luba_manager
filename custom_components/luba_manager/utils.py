def base_score(temp, rain):

    if 15 <= temp <= 28:
        t = 30
    elif 10 <= temp < 15 or 28 < temp <= 32:
        t = 15
    else:
        t = 0

    w = 25 if rain < 20 else 15 if rain < 40 else 5 if rain < 70 else 0

    return t + w