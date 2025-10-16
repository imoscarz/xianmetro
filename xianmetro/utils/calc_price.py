"""
票价计算工具模块

提供地铁票价计算功能，支持多种优惠类型。
"""


def calc_price(distance: int, discount: int = 0):
    """
    计算地铁票价

    根据乘坐距离和优惠类型计算实际票价。票价分档标准：
    - 0-6公里：2元
    - 7-10公里：3元
    - 11-14公里：4元
    - 15-20公里：5元
    - 21-26公里：6元
    - 26公里以上：每增加8公里加1元

    Args:
        distance: 乘坐距离，单位：公里
        discount: 优惠类别
            0 - 无优惠（普通票）
            1 - 地铁卡（9折）
            2 - 学生卡（5折）
            3 - 老年卡/爱心卡/拥军卡（免费）

    Returns:
        float: 票价，单位：元
    """
    # 根据距离计算基础票价
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
        price = (distance - 26) // 8 + 6

    # 应用优惠
    if discount == 0:
        return price
    elif discount == 1:
        return price * 0.9  # 地铁卡9折
    elif discount == 2:
        return price * 0.5  # 学生卡5折
    elif discount == 3 or discount == 4:
        return 0  # 老年卡/爱心卡/拥军卡免费
    else:
        return price
