import math

def haversine(lat1, lon1, lat2, lon2):
    # 经纬度转换为弧度
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0
    lat1 = lat1 * math.pi / 180.0
    lat2 = lat2 * math.pi / 180.0

    a = math.sin(dLat / 2) ** 2 + math.sin(dLon / 2) ** 2 * math.cos(lat1) * math.cos(lat2)
    rad = 6371  # 地球平均半径（公里）
    c = 2 * math.asin(math.sqrt(a))
    return rad * c