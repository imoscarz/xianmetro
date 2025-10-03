import __main__
import requests
from assets import UPDATE_LINK
import json

def get_metro_info(city = "西安"):
    """
    Fetch metro station information from AMAP API, and return it as a JSON object.
    :return: json object containing metro station information
    """
    api_url = UPDATE_LINK.get(city, UPDATE_LINK["西安"])
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(api_url,headers=headers)
    return json.loads(response.text)

def parse_metro_info(metro_json):
    """
    Parse metro station information from JSON object.
    :param metro_json: json object containing metro station information
    :return: list of dictionaries containing parsed metro station information
    """
    _metro_info = []
    lines = metro_json['l']
    for line in lines:
        line_name = line['ln']
        is_loop = line['lo']
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
            'stations': stations
        })
    return _metro_info

def save_to_file(metro_info):
    """
    Save metro station information to a JSON file.
    :param metro_info: list of dictionaries containing parsed metro station information
    """
    with open('metro_info.json', 'w', encoding='utf-8') as f:
        json.dump(metro_info, f, ensure_ascii=False, indent=4)

def load_from_file():
    """
    Load metro station information from a JSON file.
    :return: list of dictionaries containing parsed metro station information
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
    Get a list of all station IDs.
    :return: list of station IDs
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
    Get a list of all station names.
    :return: list of station names
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

if __name__ == "__main__":
    metro_json = get_metro_info()
    metro_info = parse_metro_info(metro_json)
    save_to_file(metro_info)
