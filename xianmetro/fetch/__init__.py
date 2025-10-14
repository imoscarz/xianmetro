__name__ = "fetch"
__version__ = "0.1.0"
__author__ = "imoscarz"
__description__ = "Fetch metro station information from AMAP API, or load from local file."

from .fetch_data import (
    get_metro_info,
    parse_metro_info,
    save_to_file,
    load_from_file,
    get_id_list,
    get_station_list,
    get_line_color,
)