import json
from xianmetro.station import Station, StationInLine
from xianmetro.fetch import load_from_file

def parse_stations():
    metro_data = load_from_file()
    station_dict = {}  # key: id, value: Station object
    # Temporary storage for transfer stations (id: list of StationInLine for different lines)
    transfer_map = {}

    for line_info in metro_data:
        line_name = line_info['line_name']
        is_loop = line_info.get('is_loop', "0") == "1"
        stations_data = line_info['stations']
        station_ids = list(stations_data.keys())
        n = len(station_ids)

        for idx, station_id in enumerate(station_ids):
            # Get prev/next for current station (loop if is_loop)
            prev_idx = (idx - 1) % n if is_loop else (idx - 1 if idx > 0 else None)
            next_idx = (idx + 1) % n if is_loop else (idx + 1 if idx < n - 1 else None)
            prev_station_id = station_ids[prev_idx] if prev_idx is not None else None
            next_station_id = station_ids[next_idx] if next_idx is not None else None

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
                # First occurrence, create the Station object
                station_dict[station_id] = Station(
                    name=station_name,
                    id=station_id,
                    line=[station_in_line],
                    coords=(latitude, longitude)
                )
            else:
                # Transfer station: add new line info if not already present
                # Prevent duplicate line_name in line list
                if not any(l.line_name == line_name for l in station_dict[station_id].line):
                    station_dict[station_id].line.append(station_in_line)

    return station_dict

def id_to_name(station_dict, station_id):
    station = station_dict.get(station_id)
    return station.name if station else None

def name_to_id(station_dict, station_name):
    for station in station_dict.values():
        if station.name == station_name:
            return station.id
    return None

if __name__ == "__main__":
    station_dict = parse_stations()
    # Print all stations
    for station_id, station in station_dict.items():
        print(f"Station ID: {station_id}, Name: {station.name}, Lines: {[line.line_name for line in station.line]}, Coords: {station.coords}, Siblings: {[id_to_name(station_dict,line.prev_station_id) for line in station.line]} <-> {[id_to_name(station_dict, line.next_station_id) for line in station.line]}")
    print(f"Total stations parsed: {len(station_dict)}")