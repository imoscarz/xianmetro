"""
站点数据结构模块

定义地铁站点和线路的数据模型。
"""


class StationInLine:
    """
    线路中的站点类
    
    表示某个站点在特定线路上的信息，包括前后站点关系。
    """
    
    def __init__(self, station_id, line_id, line_name,
                 prev_station_id=None, next_station_id=None):
        """
        初始化线路中的站点
        
        Args:
            station_id: 站点ID
            line_id: 线路ID
            line_name: 线路名称
            prev_station_id: 前一站点的ID（可选）
            next_station_id: 后一站点的ID（可选）
        """
        self.station_id = station_id
        self.line_id = line_id
        self.line_name = line_name
        self.prev_station_id = prev_station_id
        self.next_station_id = next_station_id


class Station:
    """
    地铁站点类
    
    表示一个地铁站点的完整信息，包括名称、位置和所属线路。
    一个站点可能属于多条线路（换乘站）。
    """
    
    def __init__(self, name, id, line, coords):
        """
        初始化地铁站点
        
        Args:
            name: 站点名称
            id: 站点ID
            line: StationInLine对象列表，表示该站点所属的所有线路
            coords: 坐标元组（纬度，经度）
            
        Raises:
            AssertionError: 如果line不是StationInLine对象列表或coords不是元组
        """
        self.name = name
        self.id = id
        assert all(isinstance(item, StationInLine) for item in line), \
            "line must be a list of StationInLine objects"
        self.line = line
        assert isinstance(coords, tuple), "coords must be a tuple"
        self.coords = coords  # (latitude, longitude)

