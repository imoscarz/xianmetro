"""
距离计算工具模块

提供基于Haversine公式的地理距离计算功能。
"""

import math


def haversine(lat1, lon1, lat2, lon2):
    """
    使用Haversine公式计算两个地理坐标点之间的距离

    该公式用于计算地球表面两点之间的最短距离（大圆距离）。

    Args:
        lat1: 第一个点的纬度
        lon1: 第一个点的经度
        lat2: 第二个点的纬度
        lon2: 第二个点的经度

    Returns:
        float: 两点之间的距离（单位：公里）
    """
    # 经纬度转换为弧度
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0
    lat1 = lat1 * math.pi / 180.0
    lat2 = lat2 * math.pi / 180.0

    a = (math.sin(dLat / 2) ** 2 +
         math.sin(dLon / 2) ** 2 * math.cos(lat1) * math.cos(lat2))
    rad = 6371  # 地球平均半径（公里）
    c = 2 * math.asin(math.sqrt(a))
    return rad * c
