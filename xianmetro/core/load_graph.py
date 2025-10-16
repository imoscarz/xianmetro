"""
图加载模块

负责从地铁数据文件中解析站点信息，构建站点图结构，提供站点ID和名称的转换功能。
"""

import json
from xianmetro.station import Station, StationInLine
from xianmetro.fetch import load_from_file


def parse_stations():
    """
    解析地铁站点数据，构建站点字典

    从本地文件加载地铁数据，为每个站点创建Station对象，
    处理换乘站（同一站点多条线路）的情况。

    Returns:
        dict: 站点ID到Station对象的映射字典
    """
    metro_data = load_from_file()
    station_dict = {}  # key: id, value: Station object
    # 换乘站临时存储（id: 不同线路的StationInLine列表）
    transfer_map = {}

    for line_info in metro_data:
        line_name = line_info['line_name']
        is_loop = line_info.get('is_loop', "0") == "1"
        stations_data = line_info['stations']
        station_ids = list(stations_data.keys())
        n = len(station_ids)

        for idx, station_id in enumerate(station_ids):
            # 获取当前站点的前后站（环线则循环）
            prev_idx = ((idx - 1) % n if is_loop
                        else (idx - 1 if idx > 0 else None))
            next_idx = ((idx + 1) % n if is_loop
                        else (idx + 1 if idx < n - 1 else None))
            prev_station_id = (station_ids[prev_idx]
                               if prev_idx is not None else None)
            next_station_id = (station_ids[next_idx]
                               if next_idx is not None else None)

            info = stations_data[station_id]
            station_name = info['station_name']
            latitude = float(info['latitude'])
            longitude = float(info['longitude'])
            line_id = info['line_id']

            station_in_line = StationInLine(
                station_id=station_id,
                line_id=line_id,
                line_name=line_name,
                prev_station_id=prev_station_id,
                next_station_id=next_station_id
            )

            if station_id not in station_dict:
                # 首次出现，创建Station对象
                station_dict[station_id] = Station(
                    name=station_name,
                    id=station_id,
                    line=[station_in_line],
                    coords=(latitude, longitude)
                )
            else:
                # 换乘站：添加新的线路信息（如果尚未存在）
                # 防止line_name重复
                if not any(l.line_name == line_name
                           for l in station_dict[station_id].line):
                    station_dict[station_id].line.append(station_in_line)

    return station_dict


def id_to_name(station_dict, station_id):
    """
    将站点ID转换为站点名称

    Args:
        station_dict: 站点字典
        station_id: 站点ID

    Returns:
        str: 站点名称，如果站点不存在则返回None
    """
    station = station_dict.get(station_id)
    return station.name if station else None


def name_to_id(station_dict, station_name):
    """
    将站点名称转换为站点ID

    Args:
        station_dict: 站点字典
        station_name: 站点名称

    Returns:
        str: 站点ID，如果站点不存在则返回None
    """
    for station in station_dict.values():
        if station.name == station_name:
            return station.id
    return None


if __name__ == "__main__":
    station_dict = parse_stations()
    # 打印所有站点信息
    for station_id, station in station_dict.items():
        print(
            f"Station ID: {station_id}, "
            f"Name: {station.name}, "
            f"Lines: {[line.line_name for line in station.line]}, "
            f"Coords: {station.coords}, "
            f"Siblings: {[id_to_name(station_dict, line.prev_station_id) for line in station.line]} "
            f"<-> {[id_to_name(station_dict, line.next_station_id) for line in station.line]}"
        )
    print(f"Total stations parsed: {len(station_dict)}")
