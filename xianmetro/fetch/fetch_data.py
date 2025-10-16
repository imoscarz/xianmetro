"""
数据获取模块

负责从高德地图API获取地铁信息，解析数据并保存到本地文件。
提供地铁站点列表、线路颜色等查询功能。
"""

import json
import requests

from xianmetro.assets import UPDATE_LINK


def get_metro_info(city="西安"):
    """
    从高德地图API获取地铁站点信息

    Args:
        city: 城市名称，默认为"西安"

    Returns:
        dict: 包含地铁站点信息的JSON对象
    """
    api_url = UPDATE_LINK.get(city, UPDATE_LINK["西安"])
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.3"
        )
    }
    response = requests.get(api_url, headers=headers)
    return json.loads(response.text)


def parse_metro_info(metro_json):
    """
    解析地铁站点JSON信息

    将从API获取的原始JSON数据转换为结构化的站点信息列表。

    Args:
        metro_json: 包含地铁站点信息的JSON对象

    Returns:
        list: 解析后的地铁站点信息列表，每个元素包含线路和站点详情
    """
    _metro_info = []
    lines = metro_json['l']
    for line in lines:
        line_name = line['ln']
        is_loop = line['lo']
        color = line['cl']
        stations = {}
        for station in line['st']:
            station_sl = station['sl'].split(',')
            station_id = station['rs']
            station_info = {
                'line': line_name,
                'station_name': station['n'],
                'line_id': station_id,
                'latitude': station_sl[1],
                'longitude': station_sl[0]
            }
            stations[station_id] = station_info
        _metro_info.append({
            'line_name': line_name,
            'is_loop': is_loop,
            'color': color,
            'stations': stations
        })
    return _metro_info


def save_to_file(metro_info):
    """
    将地铁站点信息保存到JSON文件

    Args:
        metro_info: 解析后的地铁站点信息列表
    """
    with open('metro_info.json', 'w', encoding='utf-8') as f:
        json.dump(metro_info, f, ensure_ascii=False, indent=4)


def load_from_file():
    """
    从JSON文件加载地铁站点信息

    如果文件不存在，则自动获取并保存数据。

    Returns:
        list: 解析后的地铁站点信息列表
    """
    try:
        with open('metro_info.json', 'r', encoding='utf-8') as f:
            metro_info = json.load(f)
        return metro_info
    except FileNotFoundError:
        save_to_file(parse_metro_info(get_metro_info()))
        return load_from_file()


def get_id_list():
    """
    获取所有站点ID列表

    Returns:
        list: 站点ID列表
    """
    try:
        metro_info = load_from_file()
    except Exception as e:
        metro_info = parse_metro_info(get_metro_info())
        save_to_file(metro_info)
    id_list = []
    for line in metro_info:
        for station_id in line['stations']:
            id_list.append(station_id)
    return id_list


def get_station_list():
    """
    获取所有站点名称列表

    Returns:
        list: 站点名称列表
    """
    try:
        metro_info = load_from_file()
    except Exception as e:
        metro_info = parse_metro_info(get_metro_info())
        save_to_file(metro_info)
    name_list = []
    for line in metro_info:
        for station_id in line['stations']:
            name_list.append(line['stations'][station_id]['station_name'])
    return name_list


def get_line_color(line_name):
    """
    获取地铁线路的颜色

    Args:
        line_name: 线路名称

    Returns:
        str: 线路颜色的十六进制表示（如"#FF0000"），未找到则返回"#000000"
    """
    try:
        metro_info = load_from_file()
    except Exception as e:
        metro_info = parse_metro_info(get_metro_info())
        save_to_file(metro_info)
    for line in metro_info:
        if line['line_name'] == line_name:
            return f"#{line['color']}"
    return "#000000"  # 默认颜色


if __name__ == "__main__":
    metro_json = get_metro_info()
    metro_info = parse_metro_info(metro_json)
    save_to_file(metro_info)
