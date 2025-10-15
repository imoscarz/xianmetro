"""
Map widget for displaying metro route on a canvas
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QBrush


class MapWidget(QWidget):
    """
    A simple map widget that displays metro routes using latitude/longitude coordinates
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 600)
        self.route_data = None  # Will store route information
        self.stations_dict = None  # Will store all stations information
        
    def set_route(self, route, stations_dict, line_colors):
        """
        Set the route to display
        :param route: List of route segments, each containing line name and station IDs
        :param stations_dict: Dictionary of all stations (id -> Station object)
        :param line_colors: Dictionary mapping line names to colors
        """
        self.route_data = route
        self.stations_dict = stations_dict
        self.line_colors = line_colors
        self.update()
        
    def clear_route(self):
        """Clear the current route display"""
        self.route_data = None
        self.update()
        
    def paintEvent(self, event):
        """Paint the map with route"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor("#f4f7fa"))
        
        if not self.route_data or not self.stations_dict:
            # Draw placeholder text
            painter.setPen(QColor("#999"))
            painter.setFont(QFont("Microsoft YaHei", 14))
            painter.drawText(self.rect(), Qt.AlignCenter, "请先规划路线")
            return
            
        # Collect all coordinates from the route
        all_coords = []
        for segment in self.route_data:
            for station_id in segment["stations"]:
                station = self.stations_dict.get(station_id)
                if station and station.coords and isinstance(station.coords, tuple) and len(station.coords) >= 2:
                    all_coords.append(station.coords)
                    
        if not all_coords:
            return
            
        # Calculate bounds and scaling
        lats = [c[0] for c in all_coords]
        lons = [c[1] for c in all_coords]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Add padding
        padding = 40
        width = self.width() - 2 * padding
        height = self.height() - 2 * padding
        
        # Handle edge case where all coordinates are the same
        lat_range = max_lat - min_lat if max_lat != min_lat else 0.01
        lon_range = max_lon - min_lon if max_lon != min_lon else 0.01
        
        def coord_to_point(lat, lon):
            """Convert latitude/longitude to widget coordinates"""
            x = padding + (lon - min_lon) / lon_range * width
            y = padding + (max_lat - lat) / lat_range * height  # Invert Y axis
            return QPointF(x, y)
        
        # Draw route segments
        for segment in self.route_data:
            line_name = segment["line"]
            station_ids = segment["stations"]
            color = self.line_colors.get(line_name, "#000000")
            
            # Draw lines between stations
            pen = QPen(QColor(color))
            pen.setWidth(4)
            painter.setPen(pen)
            
            for i in range(len(station_ids) - 1):
                station1 = self.stations_dict.get(station_ids[i])
                station2 = self.stations_dict.get(station_ids[i + 1])
                if (station1 and station1.coords and isinstance(station1.coords, tuple) and len(station1.coords) >= 2 and
                    station2 and station2.coords and isinstance(station2.coords, tuple) and len(station2.coords) >= 2):
                    p1 = coord_to_point(station1.coords[0], station1.coords[1])
                    p2 = coord_to_point(station2.coords[0], station2.coords[1])
                    painter.drawLine(p1, p2)
        
        # Draw station markers and labels
        for segment in self.route_data:
            line_name = segment["line"]
            station_ids = segment["stations"]
            color = self.line_colors.get(line_name, "#000000")
            
            for station_id in station_ids:
                station = self.stations_dict.get(station_id)
                if station and station.coords and isinstance(station.coords, tuple) and len(station.coords) >= 2:
                    point = coord_to_point(station.coords[0], station.coords[1])
                    
                    # Draw station circle
                    painter.setBrush(QBrush(QColor(color)))
                    painter.setPen(QPen(QColor("#ffffff"), 2))
                    painter.drawEllipse(point, 6, 6)
                    
                    # Draw station name
                    painter.setPen(QColor("#333"))
                    painter.setFont(QFont("Microsoft YaHei", 9))
                    text_rect = painter.boundingRect(0, 0, 200, 50, Qt.AlignLeft, station.name)
                    text_rect.moveCenter(point.toPoint())
                    text_rect.translate(0, 15)
                    
                    # Draw text background
                    painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(text_rect.adjusted(-3, -1, 3, 1), 3, 3)
                    
                    # Draw text
                    painter.setPen(QColor("#333"))
                    painter.drawText(text_rect, Qt.AlignCenter, station.name)
