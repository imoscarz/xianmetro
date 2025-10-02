def calc_price(distance: int, discount: int = 0):
    """
    计算地铁票价
    :param distance: 距离，单位千米
    :param discount: 优惠类别，0-无优惠，1-地铁卡，2-学生卡，3-老年卡，4-爱心卡或拥军卡
    :return: 票价，单位元
    """
    price = 0
    if distance <= 6:
        price = 2
    elif distance <= 10:
        price = 3
    elif distance <= 14:
        price = 4
    elif distance <= 20:
        price = 5
    elif distance <= 26:
        price = 6
    else:
        price = (distance - 26)//8 + 6
    if discount == 0:
        return price
    elif discount == 1:
        return price * 0.9
    elif discount == 2:
        return price * 0.5
    elif discount == 3 or discount == 4:
        return 0
    else:
        return price