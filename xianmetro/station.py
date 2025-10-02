class StationInLine:
    def __init__(self, station_id, line_id, line_name, prev_station_id = None, next_station_id = None):
        self.station_id = station_id
        self.line_id = line_id
        self.line_name = line_name
        self.prev_station_id = prev_station_id
        self.next_station_id = next_station_id

class Station:
    def __init__(self, name, id, line, coords):
        self.name = name
        self.id = id
        assert all(isinstance(item, StationInLine) for item in line), "line must be a list of StationInLine objects"
        self.line = line
        assert isinstance(coords, tuple), "coords must be a list of tuples"
        self.coords = coords  # (latitude, longitude)
