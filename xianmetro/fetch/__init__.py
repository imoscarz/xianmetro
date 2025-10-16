__name__ = "fetch"
__version__ = "0.1.0"
__author__ = "imoscarz"
__description__ = "数据获取模块，从高德地图API获取地铁站点信息或从本地文件加载。"

from .fetch_data import (
    get_metro_info,
    parse_metro_info,
    save_to_file,
    load_from_file,
    get_id_list,
    get_station_list,
    get_line_color,
)
